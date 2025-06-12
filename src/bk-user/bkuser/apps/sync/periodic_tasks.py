# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

import logging
from datetime import timedelta

from django.db.models import F, Value
from django.db.models.functions import Concat
from django.utils import timezone

from bkuser.apps.data_source.models import DataSource
from bkuser.apps.sync.constants import SyncTaskStatus, SyncTaskTrigger
from bkuser.apps.sync.data_models import DataSourceSyncConfig, DataSourceSyncOptions
from bkuser.apps.sync.managers import DataSourceSyncManager
from bkuser.apps.sync.models import DataSourceSyncTask, TenantSyncTask
from bkuser.celery import app
from bkuser.common.task import BaseTask

logger = logging.getLogger(__name__)


@app.task(base=BaseTask, ignore_result=True)
def build_and_run_data_source_sync_task(data_source_id: int, exec_time_index: int = 0):
    """同步数据源数据"""
    logger.info(
        "[celery-beat] receive build and run data source %s sync task, exec_time_index: %s",
        data_source_id,
        exec_time_index,
    )
    data_source = DataSource.objects.get(id=data_source_id)
    if data_source.is_local:
        logger.error("why local data source %s has periodic task?", data_source_id)
        return

    # 检查是否应该执行任务
    if not _should_execute_sync_task(data_source, exec_time_index):
        logger.info("[celery-beat] data source %s sync task skipped due to schedule interval", data_source_id)
        return

    sync_opts = DataSourceSyncOptions(
        # 定时执行的任务，执行者为最后修改数据源配置的人
        operator=data_source.updater,
        overwrite=True,
        incremental=False,
        # 注：现在就在异步任务中，不需要 async_run=True
        async_run=False,
        trigger=SyncTaskTrigger.CRONTAB,
    )
    DataSourceSyncManager(data_source, sync_opts).execute()

    logger.info("[celery-beat] build and run data source %s sync task end", data_source_id)


def _should_execute_sync_task(data_source: DataSource, exec_time_index: int) -> bool:
    """判断是否应该执行同步任务"""
    sync_config = DataSourceSyncConfig(**data_source.sync_config)

    exec_time = sync_config.exec_times[exec_time_index]
    should_execute = sync_config.should_execute_now(exec_time)
    if not should_execute:
        logger.info("data source %s should not execute sync task now based on period config", data_source.id)
        return False

    return True


@app.task(base=BaseTask, ignore_result=True)
def mark_running_sync_task_as_failed_if_exceed_one_day():
    """设置长时间运行的同步任务为失败"""
    logger.info("[celery-beat] start mark running sync task as failed if exceed one day")

    time_now = timezone.now()
    error_msg = "\n\nERROR sync task runs more than one day, consider it as failed."

    DataSourceSyncTask.objects.filter(
        status__in=[SyncTaskStatus.PENDING, SyncTaskStatus.RUNNING],
        start_at__lt=time_now - timedelta(days=1),
    ).update(
        status=SyncTaskStatus.FAILED,
        logs=Concat(F("logs"), Value(error_msg)),
        updated_at=time_now,
    )

    TenantSyncTask.objects.filter(
        status__in=[SyncTaskStatus.PENDING, SyncTaskStatus.RUNNING],
        start_at__lt=time_now - timedelta(days=1),
    ).update(
        status=SyncTaskStatus.FAILED,
        logs=Concat(F("logs"), Value(error_msg)),
        updated_at=time_now,
    )

    logger.info("[celery-beat] mark running sync task as failed if exceed one day end")
