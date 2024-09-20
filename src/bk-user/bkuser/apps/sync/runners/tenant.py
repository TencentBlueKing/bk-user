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

from bkuser.apps.data_source.models import DataSource
from bkuser.apps.sync.contexts import TenantSyncTaskContext
from bkuser.apps.sync.models import TenantSyncTask
from bkuser.apps.sync.signals import post_sync_tenant
from bkuser.apps.sync.syncers import TenantDepartmentSyncer, TenantUserSyncer
from bkuser.apps.tenant.constants import TenantStatus
from bkuser.apps.tenant.models import Tenant

logger = logging.getLogger(__name__)


class TenantSyncTaskRunner:
    """租户数据同步任务执行器"""

    def __init__(self, task: TenantSyncTask):
        self.task = task
        self.data_source = DataSource.objects.get(id=task.data_source_id)
        self.tenant = Tenant.objects.get(id=task.tenant_id)

    def run(self):
        if self._need_skip_sync():
            return

        with TenantSyncTaskContext(self.task) as ctx:
            self._sync_departments(ctx)
            self._sync_users(ctx)

        self._send_signal()

    def _need_skip_sync(self) -> bool:
        """租户不是启用状态，需要跳过同步"""
        if self.tenant.status != TenantStatus.ENABLED:
            logger.warning("tenant %s isn't enabled, skip tenant sync...", self.tenant.id)
            return True

        # 数据源所属租户与待同步租户相同，不需要再次检查
        if self.data_source.owner_tenant_id == self.tenant.id:
            return False

        if not Tenant.objects.filter(id=self.data_source.owner_tenant_id, status=TenantStatus.ENABLED).exists():
            logger.warning(
                "data source %s's owner tenant %s isn't enabled, skip tenant sync...",
                self.data_source.id,
                self.data_source.owner_tenant_id,
            )
            return True

        return False

    def _sync_departments(self, ctx: TenantSyncTaskContext):
        """同步部门信息"""
        TenantDepartmentSyncer(ctx, self.data_source, self.tenant).sync()

    def _sync_users(self, ctx: TenantSyncTaskContext):
        """同步用户信息"""
        TenantUserSyncer(ctx, self.data_source, self.tenant).sync()

    def _send_signal(self):
        """发送租户同步完成信号，触发后续流程"""
        post_sync_tenant.send(sender=self.__class__, tenant=self.tenant, data_source=self.data_source)
