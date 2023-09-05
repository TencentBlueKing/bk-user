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


def create_tenant_users(tenant_id: str, data_source_id: int, data_source_user_ids: List[int]) -> List[TenantUser]:
    """
    创建租户用户
    """
    tenant_users: List[TenantUser] = []
    for user_id in data_source_user_ids:
        tenant_user = TenantUser.objects.create(
            data_source_user_id=user_id,
            data_source_id=data_source_id,
            tenant_id=tenant_id,
            id=generate_uuid(),
        )
        tenant_users.append(tenant_user)
    return tenant_users


def create_tenant_departments(
    tenant_id: str, data_source_id: int, data_source_department_ids: List[int]
) -> List[TenantDepartment]:
    """
    创建租户部门
    """
    tenant_departments: List[TenantDepartment] = []
    for department in data_source_department_ids:
        tenant_department = TenantDepartment.objects.create(
            data_source_department_id=department,
            data_source_id=data_source_id,
            tenant_id=tenant_id,
        )
        tenant_departments.append(tenant_department)
    return tenant_departments
