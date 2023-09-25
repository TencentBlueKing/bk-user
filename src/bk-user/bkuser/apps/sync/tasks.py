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
from typing import Any, Dict

from bkuser.apps.data_source.initializers import LocalDataSourceIdentityInfoInitializer
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.data_source.notifier import LocalDataSourceUserNotifier
from bkuser.apps.sync.models import DataSourceSyncTask, TenantSyncTask
from bkuser.apps.sync.runners import DataSourceSyncTaskRunner, TenantSyncTaskRunner
from bkuser.celery import app
from bkuser.common.task import BaseTask
from bkuser.plugins.local.constants import NotificationScene

logger = logging.getLogger(__name__)


@app.task(base=BaseTask, ignore_result=True)
def sync_data_source(task_id: int, context: Dict[str, Any]):
    """同步数据源数据"""
    logger.info("[celery] receive data source sync task: %s", task_id)
    task = DataSourceSyncTask.objects.get(id=task_id)
    DataSourceSyncTaskRunner(task, context).run()


@app.task(base=BaseTask, ignore_result=True)
def initialize_data_source_user_identity_infos(data_source_id: int):
    """初始化数据源用户账密数据"""
    logger.info("[celery] receive data source %s user identity infos initialize task", data_source_id)
    data_source = DataSource.objects.get(id=data_source_id)
    # 为没有账密信息的用户进行初始化
    users = LocalDataSourceIdentityInfoInitializer(data_source).sync()
    # 逐一发送通知（邮件/短信）
    LocalDataSourceUserNotifier(data_source, NotificationScene.USER_INITIALIZE).send(users)


@app.task(base=BaseTask, ignore_result=True)
def sync_tenant(task_id: int):
    """同步数据源数据"""
    logger.info("[celery] receive tenant sync task: %s", task_id)
    task = TenantSyncTask.objects.get(id=task_id)
    TenantSyncTaskRunner(task).run()
