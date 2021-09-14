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
from typing import Optional

from bkuser_core.categories.constants import SyncTaskType
from bkuser_core.categories.exceptions import ExistsSyncingTaskError
from bkuser_core.categories.loader import get_plugin_by_category
from bkuser_core.categories.models import ProfileCategory, SyncTask
from bkuser_core.categories.utils import catch_time
from bkuser_core.celery import app
from bkuser_core.common.cache import clear_cache
from bkuser_core.common.error_codes import error_codes

logger = logging.getLogger(__name__)


@app.task
def adapter_sync(instance_id: int, operator: str, task_id: Optional[uuid.UUID] = None, *args, **kwargs):
    logger.info("going to sync Category<%s>", instance_id)
    instance = ProfileCategory.objects.get(pk=instance_id)

    if task_id is None:
        # 只有定时任务未传递 task_id
        try:
            task_id = SyncTask.objects.register_task(category=instance, operator=operator, type_=SyncTaskType.AUTO).id
        except ExistsSyncingTaskError as e:
            raise error_codes.LOAD_DATA_FAILED.f(str(e))

    with SyncTask.objects.get(id=task_id):
        try:
            plugin = get_plugin_by_category(instance)
        except ValueError:
            logger.exception("category type<%s> is not support", instance.type)
            raise error_codes.CATEGORY_TYPE_NOT_SUPPORTED
        except Exception:
            logger.exception(
                "load adapter<%s-%s-%s> failed",
                instance.type,
                instance.display_name,
                instance.id,
            )
            raise error_codes.LOAD_DATA_ADAPTER_FAILED

        with catch_time() as context:
            plugin.sync(instance_id=instance_id, task_id=task_id, *args, **kwargs)
        logger.info(f"同步总耗时: {context.time_delta}s, 消耗总CPU时间: {context.clock_delta}s.")

    # 标记同步
    instance.mark_synced()

    # 同步成功后，清理当前的缓存
    clear_cache()
