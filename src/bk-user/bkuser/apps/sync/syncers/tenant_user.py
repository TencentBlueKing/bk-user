# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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

# ignore custom logger must use %s string format in this file
# ruff: noqa: G004
import datetime

from django.db import transaction
from django.utils import timezone

from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.sync.constants import SyncOperation, TenantSyncObjectType
from bkuser.apps.sync.contexts import TenantSyncTaskContext
from bkuser.apps.tenant.models import Tenant, TenantUser, TenantUserValidityPeriodConfig
from bkuser.apps.tenant.utils import TenantUserIDGenerator
from bkuser.common.constants import PERMANENT_TIME


class TenantUserSyncer:
    """租户部门同步器"""

    batch_size = 250

    def __init__(self, ctx: TenantSyncTaskContext, data_source: DataSource, tenant: Tenant):
        self.ctx = ctx
        self.data_source = data_source
        self.tenant = tenant
        self.user_account_expired_at = self._get_user_account_expired_at()

    def sync(self):
        """TODO (su) 协同支持指定数据范围后，需要考虑限制"""
        exists_tenant_users = TenantUser.objects.filter(tenant=self.tenant, data_source=self.data_source)
        data_source_users = DataSourceUser.objects.filter(data_source=self.data_source)

        # 删除掉租户中存在的，但是数据源中不存在的
        waiting_delete_tenant_users = exists_tenant_users.exclude(data_source_user__in=data_source_users)

        # 数据源中存在，但是租户中不存在的，需要创建
        waiting_sync_data_source_users = data_source_users.exclude(
            id__in=[u.data_source_user_id for u in exists_tenant_users]
        )
        generator = TenantUserIDGenerator(self.tenant.id, self.data_source, prepare_batch=True)
        waiting_create_tenant_users = [
            TenantUser(
                id=generator.gen(user),
                tenant=self.tenant,
                data_source_user=user,
                data_source=self.data_source,
                account_expired_at=self.user_account_expired_at,
            )
            for user in waiting_sync_data_source_users
        ]

        # 统一在事务中对租户用户进行变更，先删除再增加
        with transaction.atomic():
            waiting_delete_tenant_users.delete()
            TenantUser.objects.bulk_create(waiting_create_tenant_users, batch_size=self.batch_size)

        # 记录删除日志，变更记录
        self.ctx.logger.info(f"delete {len(waiting_delete_tenant_users)} tenant users")
        self.ctx.recorder.add(SyncOperation.DELETE, TenantSyncObjectType.USER, waiting_delete_tenant_users)
        # 记录创建日志，变更记录
        self.ctx.logger.info(f"create {len(waiting_create_tenant_users)} tenant users")
        self.ctx.recorder.add(SyncOperation.CREATE, TenantSyncObjectType.USER, waiting_create_tenant_users)

    def _get_user_account_expired_at(self) -> datetime.datetime:
        """若存在账号有效期配置且已启用，则累加到 timezone.now() 上，否则直接返回 PERMANENT_TIME"""
        cfg = TenantUserValidityPeriodConfig.objects.filter(tenant=self.tenant).first()
        # NOTE: cfg.validity_period == -1 表示永久有效期
        if not (cfg and cfg.enabled and cfg.validity_period > 0):
            return PERMANENT_TIME

        expired_at = timezone.now() + datetime.timedelta(days=cfg.validity_period)
        return expired_at if expired_at < PERMANENT_TIME else PERMANENT_TIME
