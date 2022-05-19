# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging
import uuid
from contextlib import contextmanager
from typing import Any, Optional, Union

from celery import Task
from django.conf import settings

from bkuser_core.categories.constants import SyncTaskStatus, SyncTaskType
from bkuser_core.categories.exceptions import ExistsSyncingTaskError
from bkuser_core.categories.loader import get_plugin_by_category
from bkuser_core.categories.models import ProfileCategory, SyncTask
from bkuser_core.categories.plugins.constants import HookType
from bkuser_core.categories.utils import catch_time
from bkuser_core.celery import app
from bkuser_core.common.cache import clear_cache
from bkuser_core.common.error_codes import error_codes

logger = logging.getLogger(__name__)


class RetryWithHookTask(Task):
    """A task will retry automatically, with plugin hook executing"""

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": settings.TASK_MAX_RETRIES}
    retry_backoff = settings.RETRY_BACKOFF
    retry_jitter = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        category = ProfileCategory.objects.get(pk=kwargs["instance_id"])
        logger.info("Sync data task<%s> of category<%s> got result: %s", task_id, category, status)

        plugin = get_plugin_by_category(category)
        post_sync_hook = plugin.get_hook(HookType.POST_SYNC)
        if post_sync_hook:
            kwargs.update({"retries": self.request.retries, "category": category})
            post_sync_hook.trigger(status, kwargs)


@contextmanager
def sync_data_task(category: ProfileCategory, task_id: Union[uuid.UUID, Any], should_retry: bool):
    """同步数据任务，支持标记重试、失败、成功"""
    sync_task = SyncTask.objects.get(id=task_id)
    try:
        yield
    except Exception:
        if should_retry:
            status = SyncTaskStatus.RETRYING.value
            sync_task.retried_count += 1
        else:
            status = SyncTaskStatus.FAILED.value

        sync_task.status = status
        sync_task.save(update_fields=["retried_count", "status", "update_time"])
        raise
    else:
        # 标记同步
        category.mark_synced()
        sync_task.status = SyncTaskStatus.SUCCESSFUL.value
        sync_task.save(update_fields=["status", "update_time"])

        # 同步成功后，清理当前的缓存
        clear_cache()


@app.task(base=RetryWithHookTask)
def adapter_sync(instance_id: int, operator: str, task_id: Optional[uuid.UUID] = None, *args, **kwargs):
    logger.info("going to sync Category<%s>", instance_id)
    category = ProfileCategory.objects.get(pk=instance_id)

    if task_id is None:
        # 只有定时任务未传递 task_id
        try:
            # 查询最近的一个状态处于retrying的task;
            # 因为register_task做了防御(如果有正在运行的, 报错, 如果运行时间超过一个小时, 会设为失效后重新建一个)
            retrying_task = SyncTask.objects.get_crontab_retrying_task(category=category)
            if retrying_task:
                task_id = retrying_task.id
            else:
                task_id = SyncTask.objects.register_task(
                    category=category, operator=operator, type_=SyncTaskType.AUTO
                ).id
        except ExistsSyncingTaskError as e:
            logger.exception("register task fail, the task is already exists")
            raise error_codes.LOAD_DATA_FAILED.f(str(e))

    try:
        plugin = get_plugin_by_category(category)
    except ValueError:
        logger.exception(
            "category type<%s> is not support. [instance.id=%s, operator=%s, task_id=%s]",
            category.type,
            instance_id,
            operator,
            task_id,
        )
        raise error_codes.CATEGORY_TYPE_NOT_SUPPORTED
    except Exception:
        logger.exception(
            "load adapter<%s-%s-%s> failed",
            category.type,
            category.display_name,
            category.id,
        )
        raise error_codes.LOAD_DATA_ADAPTER_FAILED

    with sync_data_task(category, task_id, adapter_sync.request.retries < adapter_sync.max_retries):
        with catch_time() as context:
            plugin.sync(instance_id=instance_id, task_id=task_id, *args, **kwargs)
        logger.info(f"同步总耗时: {context.time_delta}s, 消耗总CPU时间: {context.clock_delta}s.")
