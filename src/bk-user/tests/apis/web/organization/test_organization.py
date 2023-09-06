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

import pytest
from bkuser.apps.data_source.models import (
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.models import Tenant, TenantDepartment, TenantManager, TenantUser
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from tests.test_utils.helpers import generate_random_string

pytestmark = pytest.mark.django_db


class TestTenantListApi:
    def test_list_tenants(
        self,
        api_client,
        bk_user,
        default_tenant,
        tenant_departments,
    ):
        resp = api_client.get(reverse("organization.tenant.list"))

        # 至少会有一个当前用户所属的租户
        current_tenant_id = bk_user.get_property("tenant_id")
        assert len(resp.data) >= 1
        assert current_tenant_id == resp.data[0]["id"]

        for tenant_info in resp.data:
            if tenant_info["id"] != current_tenant_id:
                assert not tenant_info["departments"]
            else:
                assert len(tenant_info["departments"]) >= 1


class TestTenantRetrieveUpdateApi:
    def test_retrieve_tenant(self, api_client, bk_user, default_tenant):
        tenant_id = bk_user.get_property("tenant_id")
        resp = api_client.get(
            reverse("organization.tenant.retrieve_update", kwargs={"id": bk_user.get_property("tenant_id")})
        )

        tenant = Tenant.objects.get(id=tenant_id)

        assert tenant.id == resp.data["id"]
        assert tenant.name == resp.data["name"]
        assert tenant.updated_at_display == resp.data["updated_at"]
        assert tenant.logo == resp.data["logo"]
        assert tenant.feature_flags == resp.data["feature_flags"]
        assert TenantManager.objects.filter(tenant=tenant).count() == len(resp.data["managers"])

        for item in resp.data["managers"]:
            assert TenantManager.objects.filter(tenant=tenant, tenant_user_id=item["id"]).exists()

    def test_retrieve_other_tenant(self, api_client, random_tenant):
        resp = api_client.get(reverse("organization.tenant.retrieve_update", kwargs={"id": random_tenant}))
        tenant = Tenant.objects.get(id=random_tenant)

        assert tenant.id == resp.data["id"]
        assert tenant.name == resp.data["name"]
        assert tenant.updated_at_display == resp.data["updated_at"]
        assert tenant.logo == resp.data["logo"]
        assert tenant.feature_flags == resp.data["feature_flags"]
        # 非当前用户所在租户，不返回管理员
        assert not resp.data["managers"]

    def test_retrieve_not_exist_tenant(self, api_client):
        resp = api_client.get(reverse("organization.tenant.retrieve_update", kwargs={"id": generate_random_string()}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_update_tenant(self, api_client, default_tenant, tenant_users):
        new_manager_ids = [user.id for user in tenant_users]
        update_data = {
            "id": "fake-tenant-updated",
            "name": "fake-tenant-updated",
            "logo": "aabb",
            "feature_flags": {"user_number_visible": False},
            "manager_ids": new_manager_ids,
        }
        api_client.put(reverse("organization.tenant.retrieve_update", kwargs={"id": default_tenant}), data=update_data)
        tenant = Tenant.objects.get(id=default_tenant)

        assert tenant.id != update_data["id"]
        assert tenant.name == update_data["name"]
        assert tenant.feature_flags == update_data["feature_flags"]
        assert tenant.logo == update_data["logo"]

        for new_manager in new_manager_ids:
            assert new_manager in list(
                TenantManager.objects.filter(tenant=tenant).values_list("tenant_user_id", flat=True)
            )

    def test_update_other_tenant(self, api_client, random_tenant, tenant_users):
        resp = api_client.put(
            reverse("organization.tenant.retrieve_update", kwargs={"id": random_tenant}),
            data={
                "id": "fake-tenant-updated",
                "name": "fake-tenant-updated",
                "feature_flags": {"user_number_visible": False},
                "logo": "aabb",
                "manager_ids": [user.id for user in tenant_users],
            },
        )
        # 进行更新非当前用户的租户，异常返回
        assert resp.status_code == status.HTTP_403_FORBIDDEN


class TestTenantUserListApi:
    def test_list_tenant_users(self, api_client, default_tenant, tenant_users):
        resp = api_client.get(reverse("organization.tenant.users.list", kwargs={"id": default_tenant}))

        assert TenantUser.objects.filter(tenant_id=default_tenant).count() == resp.data["count"]
        for item in resp.data["results"]:
            tenant_user = TenantUser.objects.filter(id=item["id"]).first()
            assert tenant_user is not None
            assert tenant_user.data_source_user.username == item["username"]
            assert tenant_user.data_source_user.full_name == item["full_name"]
            assert tenant_user.data_source_user.email == item["email"]
            assert tenant_user.data_source_user.phone == item["phone"]
            assert tenant_user.data_source_user.phone_country_code == item["phone_country_code"]
            assert tenant_user.data_source_user.logo == item["logo"]


class TestTenantDepartmentChildrenListApi:
    def test_retrieve_children(self, api_client, tenant_departments):
        for item in tenant_departments:
            resp = api_client.get(reverse("organization.children.list", kwargs={"id": item.id}))

            children = DataSourceDepartmentRelation.objects.get(department=item.data_source_department).get_children()
            tenant_department_children = TenantDepartment.objects.filter(
                data_source_department_id__in=children.values_list("department_id", flat=True)
            )

            assert tenant_department_children.count() == len(resp.data)
            for department in resp.data:
                tenant_department = tenant_department_children.filter(id=department["id"]).first()
                assert tenant_department is not None
                assert tenant_department.data_source_department.name == department["name"]


class TestTenantDepartmentUserListApi:
    def test_list_department_users(
        self,
        api_client: APIClient,
        tenant_departments,
        tenant_users,
    ):
        for tenant_department in tenant_departments:
            resp = api_client.get(reverse("departments.users.list", kwargs={"id": tenant_department.id}))
            resp_data = resp.data

            tenant_users = TenantUser.objects.filter(
                tenant_id=tenant_department.tenant_id,
                data_source_user_id__in=DataSourceDepartmentUserRelation.objects.filter(
                    department=tenant_department.data_source_department
                ).values_list("user_id", flat=True),
            )
            result_tenant_user_ids = [item["id"] for item in resp_data["results"]]

            assert tenant_users.count() == resp_data["count"]
            for tenant_user in tenant_users:
                assert tenant_user.id in result_tenant_user_ids


class TestTenantUserRetrieveApi:
    def test_retrieve_user(self, api_client, tenant_users):
        for tenant_user in tenant_users:
            resp = api_client.get(reverse("department.users.retrieve", kwargs={"id": tenant_user.id}))

            data_source_user = tenant_user.data_source_user

            assert tenant_user.id == resp.data["id"]
            real_account_expired_at = timezone.localtime(tenant_user.account_expired_at)
            assert real_account_expired_at.strftime("%Y-%m-%d %H:%M:%S") == resp.data["account_expired_at"]

            assert data_source_user.username == resp.data["username"]
            assert data_source_user.full_name == resp.data["full_name"]

            assert data_source_user.email == resp.data["email"]
            assert data_source_user.phone == resp.data["phone"]
            assert data_source_user.phone_country_code == resp.data["phone_country_code"]

            # 接口返回结果和数据库数据做比对
            tenant_departments = TenantDepartment.objects.filter(
                data_source_department_id=DataSourceDepartmentUserRelation.objects.filter(
                    user_id=data_source_user.id
                ).values_list("department_id", flat=True),
                tenant_id=tenant_user.tenant_id,
            )

            for department in resp.data["departments"]:
                assert department["id"] in tenant_departments

            data_source_leader_ids = DataSourceUserLeaderRelation.objects.filter(user=data_source_user).values_list(
                "leader_id", flat=True
            )
            tenant_leaders = TenantUser.objects.filter(
                data_source_user_id__in=data_source_leader_ids, tenant_id=tenant_user.tenant_id
            ).values_list("id", flat=True)
            for user in resp.data["leaders"]:
                assert user["id"] in tenant_leaders
