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
from rest_framework import status

from tests.test_utils.tenant import create_tenant

pytestmark = pytest.mark.django_db


class TestTenantListApi:
    @pytest.fixture()
    def other_tenant(self):
        return Tenant.objects.create(id="other-tenant", name="other-tenant")

    def test_list_tenants(self, api_client, bk_user):
        resp = api_client.get(reverse("organization.tenant.list"))
        # 至少会有一个当前用户所属的租户
        assert len(resp.data) >= 1
        resp_data = resp.data
        for tenant_info in resp_data:
            if tenant_info["id"] != bk_user.id:
                assert not tenant_info["departments"]
            else:
                assert len(tenant_info["departments"]) >= 1


class TestTenantRetrieveUpdateApi:
    @pytest.fixture()
    def other_tenant(self):
        return create_tenant("other_tenant")

    def test_retrieve_tenant(self, api_client, bk_user):
        tenant_id = bk_user.get_property("tenant_id")
        resp = api_client.get(reverse("organization.tenant.retrieve_update", kwargs={"id": tenant_id}))
        tenant = Tenant.objects.get(id=tenant_id)
        resp_data = resp.data
        assert tenant.id == resp_data["id"]
        assert tenant.name == resp_data["name"]
        assert tenant.updated_at_display == resp_data["updated_at"]
        assert tenant.logo == resp_data["logo"]
        assert tenant.feature_flags == resp_data["feature_flags"]
        assert TenantManager.objects.filter(tenant=tenant).count() == len(resp_data["managers"])

    def test_retrieve_other_tenant(self, api_client, other_tenant):
        resp = api_client.get(reverse("organization.tenant.retrieve_update", kwargs={"id": other_tenant.id}))
        resp_data = resp.data
        assert other_tenant.id == resp_data["id"]
        assert other_tenant.name == resp_data["name"]
        assert other_tenant.updated_at_display == resp_data["updated_at"]
        assert other_tenant.logo == resp_data["logo"]
        assert other_tenant.feature_flags == resp_data["feature_flags"]
        assert not resp_data["managers"]

    def test_retrieve_not_exist_tenant(self, api_client):
        resp = api_client.get(reverse("organization.tenant.retrieve_update", kwargs={"id": 7334}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_update_tenant(self, api_client, fake_tenant, fake_tenant_users):
        new_manager_ids = [user.id for user in fake_tenant_users]
        update_data = {
            "id": "fake-tenant-updated",
            "name": "fake-tenant-updated",
            "logo": "aabb",
            "feature_flags": {"user_number_visible": True},
            "manager_ids": new_manager_ids,
        }
        resp = api_client.put(
            reverse("organization.tenant.retrieve_update", kwargs={"id": fake_tenant.id}), data=update_data
        )
        assert resp.status_code == status.HTTP_200_OK

        tenant = Tenant.objects.get(id=fake_tenant.id)
        assert tenant.id != update_data["id"]
        assert tenant.name == update_data["name"]
        assert tenant.feature_flags == update_data["feature_flags"]
        assert tenant.logo == update_data["logo"]
        for new_manager in new_manager_ids:
            assert new_manager in list(
                TenantManager.objects.filter(tenant=tenant).values_list("tenant_user_id", flat=True)
            )

    def test_update_other_tenant(self, api_client, other_tenant, fake_tenant_users):
        resp = api_client.put(
            reverse("organization.tenant.retrieve_update", kwargs={"id": other_tenant.id}),
            data={
                "id": "fake-tenant-updated",
                "name": "fake-tenant-updated",
                "feature_flags": {},
                "logo": "aabb",
                "manager_ids": [user.id for user in fake_tenant_users],
            },
        )
        # 进行更新非当前用户的租户，异常返回
        assert resp.status_code == status.HTTP_403_FORBIDDEN


class TestTenantUserListApi:
    def test_list_tenant_users(self, api_client, fake_tenant, fake_tenant_users):
        resp = api_client.get(reverse("organization.tenant.users.list", kwargs={"id": fake_tenant.id}))
        assert TenantUser.objects.filter(tenant=fake_tenant).count() == resp.data["count"]


class TestTenantDepartmentChildrenListApi:
    def test_retrieve_children(self, api_client, fake_tenant_departments):
        for item in fake_tenant_departments:
            resp = api_client.get(reverse("organization.children.list", kwargs={"id": item.id}))
            children = DataSourceDepartmentRelation.objects.get(department=item.data_source_department).get_children()
            tenant_children = TenantDepartment.objects.filter(
                data_source_department_id__in=children.values_list("department_id", flat=True)
            )
            assert tenant_children.count() == len(resp.data)


class TestTenantDepartmentUserListApi:
    def test_list_department_users(self, api_client, fake_tenant_departments, fake_tenant_users):
        for tenant_department in fake_tenant_departments:
            resp = api_client.get(reverse("departments.users.list", kwargs={"id": tenant_department.id}))

            department_user_relationship = DataSourceDepartmentUserRelation.objects.filter(
                department=tenant_department.data_source_department
            ).values_list("user_id", flat=True)
            tenant_users = TenantUser.objects.filter(
                tenant_id=tenant_department.tenant_id, data_source_user_id__in=department_user_relationship
            )
            resp_data = resp.data
            assert tenant_users.count() == resp_data["count"]
            result_data_ids = [user["id"] for user in resp_data["results"]]
            for item in tenant_users:
                assert item.id in result_data_ids


class TestTenantUserRetrieveApi:
    def test_retrieve_user(self, api_client, fake_tenant_users):
        for tenant_user in fake_tenant_users:
            resp = api_client.get(reverse("department.users.retrieve", kwargs={"id": tenant_user.id}))

            resp_data = resp.data
            data_source_user = tenant_user.data_source_user

            assert tenant_user.id == resp_data["id"]
            assert tenant_user.account_expired_at.strftime("%Y-%m-%d %H:%M:%S") == resp_data["account_expired_at"]

            assert data_source_user.username == resp_data["username"]
            assert data_source_user.full_name == resp_data["full_name"]

            assert data_source_user.email == resp_data["email"]
            assert data_source_user.phone == resp_data["phone"]
            assert data_source_user.phone_country_code == resp_data["phone_country_code"]

            data_source_department_ids = DataSourceDepartmentUserRelation.objects.filter(
                user_id=data_source_user.id
            ).values_list("department_id", flat=True)
            tenant_departments = TenantDepartment.objects.filter(
                data_source_department_id=data_source_department_ids, tenant_id=tenant_user.id
            )
            department_flags = [
                True for department in resp_data["departments"] if department["id"] in tenant_departments
            ]
            assert all(department_flags)

            data_source_leader_ids = DataSourceUserLeaderRelation.objects.filter(user=data_source_user).values_list(
                "leader_id", flat=True
            )
            tenant_leaders = TenantUser.objects.filter(
                data_source_user_id__in=data_source_leader_ids, tenant_id=tenant_user.id
            )
            leader_flags = [True for user in resp_data["leaders"] if user["id"] in tenant_leaders]
            assert all(leader_flags)
