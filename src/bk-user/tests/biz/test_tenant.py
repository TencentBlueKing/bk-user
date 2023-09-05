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
from typing import List

import pytest
from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.biz.tenant import TenantDepartmentHandler, TenantUserHandler

pytestmark = pytest.mark.django_db


class TestTenantUserHandler:
    def test_get_tenant_user_leaders_map_by_id(self, default_tenant_users: List[TenantUser]):
        tenant_user_leader_map = TenantUserHandler.get_tenant_user_leaders_map_by_id(
            [item.id for item in default_tenant_users]
        )

        for tenant_user in default_tenant_users:
            tenant_user_leader_ids = [leader_info.id for leader_info in tenant_user_leader_map.get(tenant_user.id, [])]
            data_source_leader_ids = DataSourceUserLeaderRelation.objects.filter(
                user=tenant_user.data_source_user
            ).values_list("leader_id", flat=True)

            tenant_users = TenantUser.objects.filter(data_source_user_id__in=data_source_leader_ids)
            assert len(tenant_user_leader_ids) == tenant_users.count()
            assert not set(tenant_user_leader_ids) - set(tenant_users.values_list("id", flat=True))

    def test_get_tenant_user_departments_map_by_id(
        self,
        default_tenant: str,
        default_tenant_users: List[TenantUser],
        default_tenant_departments: List[TenantDepartment],
    ):
        tenant_user_departments_map = TenantUserHandler.get_tenant_user_departments_map_by_id(
            [user.id for user in default_tenant_users]
        )

        for tenant_user in default_tenant_users:
            tenant_departments = tenant_user_departments_map.get(tenant_user.id, [])

            tenant_departments_ids = [tenant_department.id for tenant_department in tenant_departments]
            data_source_department = TenantDepartment.objects.filter(
                id__in=tenant_departments_ids, tenant=default_tenant
            )

            user_related_department = DataSourceDepartmentUserRelation.objects.filter(
                user_id=tenant_user.data_source_user_id
            )

            assert not set(user_related_department.values_list("department_id", flat=True)) - set(
                data_source_department.values_list("data_source_department_id", flat=True)
            )

    def test_get_tenant_user_ids_by_tenant(self, default_tenant: str):
        tenant_user_ids = TenantUserHandler.get_tenant_user_ids_by_tenant(default_tenant)

        assert len(tenant_user_ids) == TenantUser.objects.filter(tenant=default_tenant).count()
        assert not set(tenant_user_ids) - set(
            TenantUser.objects.filter(tenant=default_tenant).values_list("id", flat=True)
        )


class TestTenantDepartmentHandler:
    def test_convert_data_source_department_to_tenant_department(
        self,
        default_tenant: str,
        local_data_source_departments: List[DataSourceDepartment],
        default_tenant_departments: List[TenantDepartment],
    ):
        data_source_department_ids = [department.id for department in local_data_source_departments]
        tenant_departments = TenantDepartmentHandler.convert_data_source_department_to_tenant_department(
            default_tenant, data_source_department_ids
        )
        assert len(data_source_department_ids) == len(tenant_departments)

        for department in tenant_departments:
            tenant_department = TenantDepartment.objects.get(id=department.id)
            assert tenant_department.data_source_department_id in data_source_department_ids
            assert department.name == tenant_department.data_source_department.name

            children_id = (
                DataSourceDepartmentRelation.objects.get(department=tenant_department.data_source_department)
                .get_children()
                .values_list("department_id", flat=True)
            )

            tenant_children_departments = TenantDepartment.objects.filter(data_source_department_id__in=children_id)
            assert department.has_children == tenant_children_departments.exists()

    @pytest.mark.parametrize(
        "not_exist_data_source_department_ids",
        [
            [],
            [1, 2, 3],
            [11, 22, 33],
            [14, 24, 34],
        ],
    )
    def test_not_exist_convert_data_source_department_to_tenant_department(
        self, default_tenant, not_exist_data_source_department_ids: List[int]
    ):
        tenant_departments = TenantDepartmentHandler.convert_data_source_department_to_tenant_department(
            default_tenant, not_exist_data_source_department_ids
        )
        assert not tenant_departments
