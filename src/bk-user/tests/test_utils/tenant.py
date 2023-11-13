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
from typing import List, Optional

from bkuser.apps.data_source.models import DataSource, DataSourceDepartment, DataSourceUser
from bkuser.apps.tenant.models import Tenant, TenantDepartment, TenantUser
from bkuser.biz.data_source_plugin import DefaultPluginConfigProvider
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.utils.uuid import generate_uuid

# 默认租户 ID & 名称
DEFAULT_TENANT = "default"


def create_tenant(tenant_id: Optional[str] = DEFAULT_TENANT) -> Tenant:
    """创建租户 & 初始化默认本地数据源"""
    tenant, _ = Tenant.objects.get_or_create(
        id=tenant_id,
        defaults={
            "name": tenant_id,
            "is_default": bool(tenant_id == DEFAULT_TENANT),
            "feature_flags": {"user_number_visible": True},
        },
    )

    plugin_config = DefaultPluginConfigProvider().get(DataSourcePluginEnum.LOCAL)
    assert plugin_config is not None

    DataSource.objects.get_or_create(
        owner_tenant_id=tenant_id,
        plugin_id=DataSourcePluginEnum.LOCAL,
        name=f"{tenant_id}-default-local",
        plugin_config=plugin_config.model_dump(),
    )
    return tenant


def create_tenant_users(tenant: Tenant, data_source_users: List[DataSourceUser]) -> List[TenantUser]:
    """创建租户用户"""

    # FIXME (su) existed_tenant_users 变量名不准确，且 data_source_users 数据不应该有冲突
    existed_tenant_users = TenantUser.objects.filter(tenant=tenant).values_list("data_source_user_id", flat=True)

    tenant_users = [
        TenantUser(
            data_source_user=user,
            data_source=user.data_source,
            tenant=tenant,
            id=generate_uuid(),
        )
        for user in data_source_users
        if user.id not in existed_tenant_users
    ]
    TenantUser.objects.bulk_create(tenant_users)
    return TenantUser.objects.filter(tenant=tenant)


def create_tenant_departments(
    tenant: Tenant, data_source_departments: List[DataSourceDepartment]
) -> List[TenantDepartment]:
    """创建租户部门"""

    tenant_departments = [
        TenantDepartment(
            data_source_department=department,
            data_source=department.data_source,
            tenant=tenant,
        )
        for department in data_source_departments
    ]
    TenantDepartment.objects.bulk_create(tenant_departments)
    return TenantDepartment.objects.filter(tenant=tenant)
