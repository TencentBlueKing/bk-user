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
from typing import Optional

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.sync.constants import SyncTaskTrigger
from bkuser.apps.sync.data_models import TenantSyncOptions
from bkuser.apps.sync.managers import TenantSyncManager
from bkuser.apps.tenant.models import Tenant
from bkuser.plugins.base import get_default_plugin_cfg
from bkuser.plugins.constants import DataSourcePluginEnum

# 默认租户 ID & 名称
DEFAULT_TENANT = "default"


def create_tenant(tenant_id: Optional[str] = DEFAULT_TENANT) -> Tenant:
    """创建租户 & 初始化默认本地数据源"""
    tenant, _ = Tenant.objects.get_or_create(
        id=tenant_id,
        defaults={
            "name": tenant_id,
            "is_default": bool(tenant_id == DEFAULT_TENANT),
        },
    )

    plugin_config = get_default_plugin_cfg(DataSourcePluginEnum.LOCAL)
    assert plugin_config is not None

    DataSource.objects.get_or_create(
        owner_tenant_id=tenant_id,
        plugin_id=DataSourcePluginEnum.LOCAL,
        type=DataSourceTypeEnum.BUILTIN_MANAGEMENT,
        defaults={"plugin_config": plugin_config},
    )
    return tenant


def sync_users_depts_to_tenant(tenant: Tenant, data_source: DataSource) -> None:
    """将数据源数据同步到租户下（租户用户 & 租户部门）"""
    sync_opts = TenantSyncOptions(operator="unittest", async_run=False, trigger=SyncTaskTrigger.MANUAL)
    TenantSyncManager(data_source, tenant.id, sync_opts).execute()
