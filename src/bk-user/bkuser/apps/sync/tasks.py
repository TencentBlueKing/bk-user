# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
from typing import Any, Dict

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.initializers import LocalDataSourceIdentityInfoInitializer
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.notification.constants import NotificationScene
from bkuser.apps.notification.notifier import TenantUserNotifier
from bkuser.apps.sync.constants import SyncTaskStatus
from bkuser.apps.sync.models import DataSourceSyncTask, TenantSyncTask
from bkuser.apps.sync.runners import DataSourceSyncTaskRunner, TenantSyncTaskRunner
from bkuser.apps.sync.workbook_temp_store import WorkbookTempStore
from bkuser.apps.tenant.models import TenantUser
from bkuser.celery import app
from bkuser.common.task import BaseTask

logger = logging.getLogger(__name__)


@app.task(base=BaseTask, ignore_result=True)
def sync_data_source(task_id: int, plugin_init_extra_kwargs: Dict[str, Any]):
    """同步数据源数据"""
    logger.info("[celery] receive data source sync task: %s", task_id)
    task = DataSourceSyncTask.objects.get(id=task_id)

    if task.data_source.is_local and (temporary_storage_id := plugin_init_extra_kwargs.get("temporary_storage_id")):
        # 若已指定临时存储的数据唯一标识，则需要从临时存储中获取数据
        storage = WorkbookTempStore()
        try:
            workbook = storage.get_once(temporary_storage_id)
        except ValueError:
            task.status = SyncTaskStatus.FAILED
            task.logs = f"data source sync task {task_id} require raw data in temporary storage, but not found"
            task.save(update_fields=["status", "logs", "updated_at"])
            return

        plugin_init_extra_kwargs = {"workbook": workbook}

    DataSourceSyncTaskRunner(task, plugin_init_extra_kwargs).run()


@app.task(base=BaseTask, ignore_result=True)
def sync_tenant(task_id: int):
    """同步数据源数据"""
    logger.info("[celery] receive tenant sync task: %s", task_id)
    task = TenantSyncTask.objects.get(id=task_id)
    TenantSyncTaskRunner(task).run()


@app.task(base=BaseTask, ignore_result=True)
def initialize_identity_info_and_send_notification(data_source_id: int):
    """初始化数据源用户账密数据（仅限于未初始化的用户）"""
    logger.info("[celery] receive identity info initialize task, data_source %s", data_source_id)
    data_source = DataSource.objects.get(id=data_source_id)
    # 非本地数据源直接跳过
    if not data_source.is_local:
        logger.debug("not local data source, skip initialize user identity infos")
        return
    # 只有能登录的数据源，才需要初始化 & 发送通知
    if data_source.type not in [DataSourceTypeEnum.REAL, DataSourceTypeEnum.BUILTIN_MANAGEMENT]:
        logger.debug("not real or builtin management data source, skip initialize user identity infos")
        return

    initializer = LocalDataSourceIdentityInfoInitializer(data_source)
    # 批量为没有账密信息的用户进行初始化
    data_source_users, user_passwd_map = initializer.initialize()

    # 逐一发送通知（邮件/短信），只会通知给非协同产生的租户用户
    tenant_users = TenantUser.objects.filter(
        tenant_id=data_source.owner_tenant_id, data_source_user__in=data_source_users
    ).select_related("data_source_user")
    TenantUserNotifier(
        NotificationScene.USER_INITIALIZE,
        data_source_id=data_source.id,
    ).batch_send(tenant_users, user_passwd_map=user_passwd_map)
