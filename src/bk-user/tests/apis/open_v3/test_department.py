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
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
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
class TestTenantDepartmentListApi:
    def test_standard(self, api_client):
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        dept_b = TenantDepartment.objects.get(data_source_department__name="部门B")
        center_aa = TenantDepartment.objects.get(data_source_department__name="中心AA")
        center_ab = TenantDepartment.objects.get(data_source_department__name="中心AB")
        center_ba = TenantDepartment.objects.get(data_source_department__name="中心BA")
        group_aaa = TenantDepartment.objects.get(data_source_department__name="小组AAA")
        group_aba = TenantDepartment.objects.get(data_source_department__name="小组ABA")
        group_baa = TenantDepartment.objects.get(data_source_department__name="小组BAA")

        resp = api_client.get(reverse("open_v3.tenant_department.list"))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 9
        assert len(resp.data["results"]) == 9
        assert [x["id"] for x in resp.data["results"]] == [
            company.id,
            dept_a.id,
            dept_b.id,
            center_aa.id,
            center_ab.id,
            center_ba.id,
            group_aaa.id,
            group_aba.id,
            group_baa.id,
        ]
        assert [x["name"] for x in resp.data["results"]] == [
            "公司",
            "部门A",
            "部门B",
            "中心AA",
            "中心AB",
            "中心BA",
            "小组AAA",
            "小组ABA",
            "小组BAA",
        ]
        assert [x["parent_id"] for x in resp.data["results"]] == [
            None,
            company.id,
            company.id,
            dept_a.id,
            dept_a.id,
            dept_b.id,
            center_aa.id,
            center_ab.id,
            center_ba.id,
        ]


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantDepartmentDescendantListApi:
    def test_with_not_level(self, api_client):
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        dept_b = TenantDepartment.objects.get(data_source_department__name="部门B")
        resp = api_client.get(reverse("open_v3.tenant_department.descendant.list", kwargs={"id": company.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 2
        assert [t["id"] for t in resp.data["results"]] == [dept_a.id, dept_b.id]
        assert [t["name"] for t in resp.data["results"]] == ["部门A", "部门B"]
        assert [t["parent_id"] for t in resp.data["results"]] == [company.id, company.id]

    def test_with_level(self, api_client):
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        center_aa = TenantDepartment.objects.get(data_source_department__name="中心AA")
        center_ab = TenantDepartment.objects.get(data_source_department__name="中心AB")
        group_aaa = TenantDepartment.objects.get(data_source_department__name="小组AAA")
        group_aba = TenantDepartment.objects.get(data_source_department__name="小组ABA")
        resp = api_client.get(
            reverse("open_v3.tenant_department.descendant.list", kwargs={"id": dept_a.id}), data={"max_level": 2}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 4
        assert [t["id"] for t in resp.data["results"]] == [center_aa.id, center_ab.id, group_aaa.id, group_aba.id]
        assert [t["name"] for t in resp.data["results"]] == ["中心AA", "中心AB", "小组AAA", "小组ABA"]
        assert [t["parent_id"] for t in resp.data["results"]] == [dept_a.id, dept_a.id, center_aa.id, center_ab.id]

    def test_with_root_department(self, api_client):
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        resp = api_client.get(reverse("open_v3.tenant_department.descendant.list", kwargs={"id": 0}))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert [t["id"] for t in resp.data["results"]] == [company.id]
        assert [t["name"] for t in resp.data["results"]] == ["公司"]
        assert [t["parent_id"] for t in resp.data["results"]] == [None]

    def test_root_department_with_level(self, api_client):
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        dept_b = TenantDepartment.objects.get(data_source_department__name="部门B")
        resp = api_client.get(
            reverse("open_v3.tenant_department.descendant.list", kwargs={"id": 0}), data={"max_level": 2}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 3
        assert {t["id"] for t in resp.data["results"]} == {company.id, dept_a.id, dept_b.id}
        assert {t["name"] for t in resp.data["results"]} == {"公司", "部门A", "部门B"}
        assert {t["parent_id"] for t in resp.data["results"]} == {None, company.id}

    def test_with_pagination(self, api_client):
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        resp = api_client.get(
            reverse("open_v3.tenant_department.descendant.list", kwargs={"id": company.id}),
            data={"max_level": 2, "page": 1, "page_size": 2},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 5
        assert len(resp.data["results"]) == 2

    def test_with_not_descendant(self, api_client):
        group_aaa = TenantDepartment.objects.get(data_source_department__name="小组AAA")
        resp = api_client.get(reverse("open_v3.tenant_department.descendant.list", kwargs={"id": group_aaa.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 0
        assert len(resp.data["results"]) == 0

    def test_with_invalid_level(self, api_client):
        company = TenantDepartment.objects.get(data_source_department__name="公司")
        resp = api_client.get(
            reverse("open_v3.tenant_department.descendant.list", kwargs={"id": company.id}), data={"max_level": -1}
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_with_department_not_found(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_department.descendant.list", kwargs={"id": 9999}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantDepartmentUserListApi:
    def test_with_standard(self, api_client):
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        lisi = TenantUser.objects.get(data_source_user__username="lisi")
        wangwu = TenantUser.objects.get(data_source_user__username="wangwu")

        resp = api_client.get(reverse("open_v3.tenant_department.user.list", kwargs={"id": dept_a.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 2
        assert {t["bk_username"] for t in resp.data["results"]} == {lisi.id, wangwu.id}
        assert {t["display_name"] for t in resp.data["results"]} == {"lisi(李四)", "wangwu(王五)"}
        assert {t["full_name"] for t in resp.data["results"]} == {"李四", "王五"}

    def test_with_department_not_found(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_department.user.list", kwargs={"id": 9999}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantDepartmentLookupApi:
    def test_with_not_org_path(self, api_client, random_tenant):
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        center_aa = TenantDepartment.objects.get(data_source_department__name="中心AA")

        resp = api_client.get(
            reverse("open_v3.tenant_department.lookup"),
            data={"department_ids": ",".join([str(dept_a.id), str(center_aa.id)])},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["id"] for t in resp.data} == {dept_a.id, center_aa.id}
        assert {t["name"] for t in resp.data} == {"部门A", "中心AA"}

    def test_with_org_path(self, api_client, random_tenant):
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A")
        center_aa = TenantDepartment.objects.get(data_source_department__name="中心AA")

        resp = api_client.get(
            reverse("open_v3.tenant_department.lookup"),
            data={"department_ids": ",".join([str(dept_a.id), str(center_aa.id)]), "with_organization_path": True},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {d["organization_path"] for d in resp.data} == {"公司", "公司/部门A"}

    def test_with_not_match(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_department.lookup"), data={"department_ids": "123456"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0
