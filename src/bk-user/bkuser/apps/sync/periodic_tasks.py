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

from bkuser.apps.data_source.constants import DataSourceStatus
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.sync.constants import SyncTaskTrigger
from bkuser.apps.sync.data_models import DataSourceSyncOptions
from bkuser.apps.sync.managers import DataSourceSyncManager
from bkuser.celery import app
from bkuser.common.task import BaseTask

logger = logging.getLogger(__name__)


@app.task(base=BaseTask, ignore_result=True)
def build_and_run_data_source_sync_task(data_source_id: int):
    """同步数据源数据"""
    logger.info("[celery-beat] receive build and run data source %s sync task", data_source_id)

    data_source = DataSource.objects.get(id=data_source_id)
    if data_source.is_local:
        logger.error("why local data source %s has periodic task?", data_source_id)
        return

    if data_source.status != DataSourceStatus.ENABLED:
        logger.warning("data source %s isn't enabled, skip...", data_source_id)
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
