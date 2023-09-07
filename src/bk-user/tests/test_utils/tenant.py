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

from bkuser.apps.tenant.models import Tenant, TenantDepartment, TenantUser
from bkuser.utils.uuid import generate_uuid

# 默认租户 ID & 名称
DEFAULT_TENANT = "default"


def create_tenant(tenant_id: Optional[str] = DEFAULT_TENANT) -> Tenant:
    """
    创建租户
    """
    tenant, _ = Tenant.objects.get_or_create(
        id=tenant_id,
        defaults={
            "name": tenant_id,
            "is_default": bool(tenant_id == DEFAULT_TENANT),
            "feature_flags": {"user_number_visible": True},
        },
    )
    return tenant


def create_tenant_users(tenant, data_source_users) -> List[TenantUser]:
    """
    创建租户用户
    """
    # 避免重复创建
    tenant_users = TenantUser.objects.filter(tenant_id=tenant, data_source_user__in=data_source_users)
    if tenant_users.exists():
        return list(tenant_users)
    tenant_users = [
        TenantUser(
            data_source_user=user,
            data_source=user.data_source,
            tenant_id=tenant,
            id=generate_uuid(),
        )
        for user in data_source_users
    ]
    TenantUser.objects.bulk_create(tenant_users)
    return list(TenantUser.objects.filter(tenant_id=tenant, data_source_user__in=data_source_users))


def create_tenant_departments(tenant, data_source_departments) -> List[TenantDepartment]:
    """
    创建租户部门
    """
    # 避免重复创建
    tenant_departments = TenantDepartment.objects.filter(
        tenant_id=tenant, data_source_department__in=data_source_departments
    )
    if tenant_departments.exists():
        return list(tenant_departments)

    tenant_departments = [
        TenantDepartment(
            data_source_department=department,
            data_source=department.data_source,
            tenant_id=tenant,
        )
        for department in data_source_departments
    ]
    TenantDepartment.objects.bulk_create(tenant_departments)
    return list(TenantDepartment.objects.filter(tenant_id=tenant, data_source_department__in=data_source_departments))
