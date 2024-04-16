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
from bkuser.apps.tenant.models import TenantDepartment
from django.urls import reverse
from rest_framework import status

from tests.test_utils.helpers import generate_random_string

pytestmark = pytest.mark.django_db


class TestTenantDepartmentListApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_list_root_depts(self, api_client, random_tenant):
        """当前租户的根部门"""
        resp = api_client.get(
            reverse(
                "organization.tenant_department.list_create",
                kwargs={"id": random_tenant.id},
            ),
            data={"parent_department_id": 0},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1

        first_dept = resp.data[0]
        excepted_dept = TenantDepartment.objects.get(
            data_source_department__name="公司",
            data_source__owner_tenant_id=random_tenant.id,
        )
        assert first_dept["id"] == excepted_dept.id
        assert first_dept["name"] == excepted_dept.data_source_department.name
        assert first_dept["has_children"] is True

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_list_sub_depts(self, api_client, random_tenant):
        """当前租户的某级子部门"""
        company = TenantDepartment.objects.get(
            data_source_department__name="公司",
            data_source__owner_tenant_id=random_tenant.id,
        )
        resp = api_client.get(
            reverse(
                "organization.tenant_department.list_create",
                kwargs={"id": random_tenant.id},
            ),
            data={"parent_department_id": company.id},
        )

        excepted_depts = TenantDepartment.objects.filter(
            data_source_department__name__contains="部门",
            data_source__owner_tenant_id=random_tenant.id,
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == excepted_depts.count()
        assert {d["id"] for d in resp.data} == set(excepted_depts.values_list("id", flat=True))
        assert {d["name"] for d in resp.data} == {"部门A", "部门B"}
        assert all(d["has_children"] for d in resp.data)

    @pytest.mark.usefixtures("_init_collaborative_users_depts")
    def test_list_collaborative_root_depts(self, api_client, collaborative_tenant):
        """某协作租户的根部门"""
        resp = api_client.get(
            reverse(
                "organization.tenant_department.list_create",
                kwargs={"id": collaborative_tenant.id},
            ),
            data={"parent_department_id": 0},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1

        excepted_dept = TenantDepartment.objects.get(
            data_source_department__name="公司",
            data_source__owner_tenant_id=collaborative_tenant.id,
        )
        assert resp.data[0]["id"] == excepted_dept.id

    @pytest.mark.usefixtures("_init_collaborative_users_depts")
    def test_list_collaborative_sub_depts(self, api_client, collaborative_tenant):
        """某协作租户的某级子部门"""
        dept_a = TenantDepartment.objects.get(
            data_source_department__name="部门A",
            data_source__owner_tenant_id=collaborative_tenant.id,
        )
        resp = api_client.get(
            reverse(
                "organization.tenant_department.list_create",
                kwargs={"id": collaborative_tenant.id},
            ),
            data={"parent_department_id": dept_a.id},
        )

        excepted_depts = TenantDepartment.objects.filter(
            data_source_department__name__contains="中心A",
            data_source__owner_tenant_id=collaborative_tenant.id,
        )
        assert resp.status_code == status.HTTP_200_OK
        assert {d["id"] for d in resp.data} == set(excepted_depts.values_list("id", flat=True))


class TestTenantDepartmentCreateApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_standard(self, api_client, random_tenant):
        url = reverse("organization.tenant_department.list_create", kwargs={"id": random_tenant.id})

        # 创建根部门
        resp = api_client.post(url, data={"parent_department_id": 0, "name": generate_random_string()})
        assert resp.status_code == status.HTTP_201_CREATED

        # 创建子部门
        company = TenantDepartment.objects.get(data_source_department__name="公司", tenant=random_tenant)
        resp = api_client.post(url, data={"parent_department_id": company.id, "name": generate_random_string()})
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_without_data_source(self, api_client, random_tenant):
        url = reverse("organization.tenant_department.list_create", kwargs={"id": random_tenant.id})
        resp = api_client.post(url, data={"parent_department_id": 0, "name": generate_random_string()})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "租户数据源不存在" in resp.data["message"]

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_create_with_invalid_parent_id(self, api_client, random_tenant):
        url = reverse("organization.tenant_department.list_create", kwargs={"id": random_tenant.id})
        resp = api_client.post(url, data={"parent_department_id": 10**7, "name": generate_random_string()})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "指定的父部门在当前租户中不存在" in resp.data["message"]

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_create_with_duplicate_name(self, api_client, random_tenant):
        company = TenantDepartment.objects.get(data_source_department__name="公司", tenant=random_tenant)
        url = reverse("organization.tenant_department.list_create", kwargs={"id": random_tenant.id})

        # duplicate with brother
        resp = api_client.post(url, data={"parent_department_id": company.id, "name": "部门A"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "父部门下已存在同名部门" in resp.data["message"]

        # duplicate with ancestor
        resp = api_client.post(url, data={"parent_department_id": company.id, "name": "公司"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "上级部门中存在同名部门" in resp.data["message"]

    def test_create_other_tenant_dept(self, api_client, random_tenant, collaborative_tenant):
        url = reverse("organization.tenant_department.list_create", kwargs={"id": collaborative_tenant.id})
        resp = api_client.post(url, data={"parent_department_id": 0, "name": generate_random_string()})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "仅可创建属于当前租户的部门" in resp.data["message"]


class TestTenantDepartmentUpdateApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_standard(self, api_client, random_tenant):
        company = TenantDepartment.objects.get(data_source_department__name="公司", tenant=random_tenant)
        url = reverse("organization.tenant_department.update_destroy", kwargs={"id": company.id})
        resp = api_client.put(url, data={"name": "总公司"})
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        company.refresh_from_db()
        assert company.data_source_department.name == "总公司"

    def test_update_invalid_dept(self, api_client):
        url = reverse("organization.tenant_department.update_destroy", kwargs={"id": 10**7})
        resp = api_client.put(url, data={"name": generate_random_string()})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_update_with_duplicate_name(self, api_client, random_tenant):
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A", tenant=random_tenant)
        url = reverse("organization.tenant_department.update_destroy", kwargs={"id": dept_a.id})

        # duplicate_with_self is ok
        resp = api_client.put(url, data={"name": "部门A"})
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        # duplicate with brother
        resp = api_client.put(url, data={"name": "部门B"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "父部门下已存在同名部门" in resp.data["message"]

        # duplicate with ancestor
        resp = api_client.put(url, data={"name": "公司"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "上级部门中存在同名部门" in resp.data["message"]


class TestTenantDepartmentDestroyApi:
    def test_standard(self):
        # TODO 等功能实现后再补充单元测试
        ...
