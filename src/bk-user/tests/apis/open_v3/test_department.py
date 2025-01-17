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

import pytest
from bkuser.apps.tenant.models import TenantDepartment
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantDepartmentRetrieveApi:
    def test_with_no_ancestors(self, api_client):
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        resp = api_client.get(
            reverse("open_v3.tenant_department.retrieve", kwargs={"id": company.id}), data={"with_ancestors": True}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == company.id
        assert resp.data["name"] == "公司"
        assert resp.data["ancestors"] == []

    def test_with_not_ancestors(self, api_client):
        center_aa = TenantDepartment.objects.get(data_source_department__name="中心AA")
        resp = api_client.get(reverse("open_v3.tenant_department.retrieve", kwargs={"id": center_aa.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == center_aa.id
        assert resp.data["name"] == "中心AA"
        assert "ancestors" not in resp.data

    def test_with_ancestors(self, api_client):
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        center_aa = TenantDepartment.objects.get(data_source_department__name="中心AA")
        resp = api_client.get(
            reverse("open_v3.tenant_department.retrieve", kwargs={"id": center_aa.id}), data={"with_ancestors": True}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == center_aa.id
        assert resp.data["name"] == "中心AA"
        assert resp.data["ancestors"] == [{"id": company.id, "name": "公司"}, {"id": dept_a.id, "name": "部门A"}]

    def test_with_not_found(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_department.retrieve", kwargs={"id": 9999}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantDepartmentChildrenListApi:
    def test_with_no_recursive(self, api_client):
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        dept_b = TenantDepartment.objects.get(data_source_department__name="部门B")
        resp = api_client.get(reverse("open_v3.tenant_department.children.list", kwargs={"id": company.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 2
        assert [t["id"] for t in resp.data["results"]] == [dept_a.id, dept_b.id]
        assert [t["name"] for t in resp.data["results"]] == ["部门A", "部门B"]

    def test_with_recursive(self, api_client):
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        center_aa = TenantDepartment.objects.get(data_source_department__name="中心AA")
        center_ab = TenantDepartment.objects.get(data_source_department__name="中心AB")
        group_aaa = TenantDepartment.objects.get(data_source_department__name="小组AAA")
        group_aba = TenantDepartment.objects.get(data_source_department__name="小组ABA")
        resp = api_client.get(
            reverse("open_v3.tenant_department.children.list", kwargs={"id": dept_a.id}), data={"is_recursive": True}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 4
        assert [t["id"] for t in resp.data["results"]] == [center_aa.id, group_aaa.id, center_ab.id, group_aba.id]
        assert [t["name"] for t in resp.data["results"]] == ["中心AA", "小组AAA", "中心AB", "小组ABA"]

    def test_with_pagination(self, api_client):
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        resp = api_client.get(
            reverse("open_v3.tenant_department.children.list", kwargs={"id": company.id}),
            data={"is_recursive": True, "page": 1, "page_size": 2},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 8
        assert len(resp.data["results"]) == 2

    def test_with_not_found(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_department.children.list", kwargs={"id": 9999}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND
