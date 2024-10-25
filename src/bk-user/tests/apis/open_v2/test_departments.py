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


class TestListDepartments:
    def test_standard(self, api_client, local_data_source, collaboration_data_source):
        resp = api_client.get(reverse("open_v2.list_departments"), data={"page": 1, "page_size": 10})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 18  # noqa: PLR2004
        assert len(resp.data["results"]) == 10  # noqa: PLR2004
        # 没有指定 with_ancestors 时，没有 children，ancestors 字段
        assert "children" not in resp.data["results"][0]
        assert "ancestors" not in resp.data["results"][0]

    def test_list_with_fields(self, api_client, local_data_source):
        resp = api_client.get(
            reverse("open_v2.list_departments"),
            data={"lookup_field": "name", "exact_lookups": "中心AB", "fields": "name,level"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert resp.data["results"][0] == {"name": "中心AB", "level": 2}

    def test_list_with_ancestors(self, api_client, local_data_source):
        resp = api_client.get(
            reverse("open_v2.list_departments"),
            data={"with_ancestors": True, "lookup_field": "name", "exact_lookups": "中心AB"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1

        center_ab = resp.data["results"][0]
        assert center_ab["name"] == "中心AB"
        assert {d["name"] for d in center_ab["ancestors"]} == {"公司", "部门A"}
        assert {d["name"] for d in center_ab["children"]} == {"小组ABA"}

    @pytest.mark.parametrize(
        ("lookup_field", "lookup_value", "result_count"),
        [("name", "中心AA", 1), ("name", "小组A", 0), ("level", "0", 1), ("level", "1", 2), ("level", "2", 3)],
    )
    def test_exact_lookups(self, api_client, local_data_source, lookup_field, lookup_value, result_count):
        resp = api_client.get(
            reverse("open_v2.list_departments"),
            data={"lookup_field": lookup_field, "exact_lookups": lookup_value},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == result_count

    @pytest.mark.parametrize(
        ("lookup_field", "lookup_value", "result_count"),
        [("name", "中心A", 2), ("name", "小组", 3), ("name", "小组A", 2)],
    )
    def test_fuzzy_lookups(self, api_client, local_data_source, lookup_field, lookup_value, result_count):
        resp = api_client.get(
            reverse("open_v2.list_departments"),
            data={"lookup_field": "name", "fuzzy_lookups": lookup_value},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == result_count

    def test_fuzzy_lookups_without_name_field(self, api_client):
        resp = api_client.get(reverse("open_v2.list_departments"), data={"lookup_field": "id", "fuzzy_lookups": "1"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "fuzzy_lookups only supported when lookup_field is name" in resp.data["message"]

    def test_no_page(self, api_client, local_data_source):
        resp = api_client.get(reverse("open_v2.list_departments"), data={"page": 1, "page_size": 5, "no_page": True})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 9  # noqa: PLR2004


class TestRetrieveDepartment:
    def test_retrieve(self, api_client, default_tenant, local_data_source):
        company = TenantDepartment.objects.get(data_source_department__name="公司", tenant=default_tenant)
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A", tenant=default_tenant)
        resp = api_client.get(
            reverse("open_v2.retrieve_department", kwargs={"id": dept_a.id}), data={"with_ancestors": True}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == dept_a.id
        assert resp.data["name"] == "部门A"
        assert resp.data["category_id"] == local_data_source.id
        # 没有指定 fields 参数时，会返回 parent，level 等字段
        assert resp.data["parent"] == company.id
        assert resp.data["level"] == 1
        assert resp.data["full_name"] == "公司/部门A"
        assert resp.data["has_children"] is True
        assert {d["name"] for d in resp.data["children"]} == {"中心AA", "中心AB"}
        assert {d["name"] for d in resp.data["ancestors"]} == {"公司"}

    def test_retrieve_with_fields(self, api_client, default_tenant, local_data_source):
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A", tenant=default_tenant)
        resp = api_client.get(
            reverse("open_v2.retrieve_department", kwargs={"id": dept_a.id}),
            data={"fields": "id,name,category_id,parent,level"},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data.keys() == {"id", "name", "category_id", "parent", "level"}

    def test_with_invalid_dept_id(self, api_client):
        resp = api_client.get(reverse("open_v2.retrieve_department", kwargs={"id": "404"}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestListDepartmentChildren:
    def test_standard(self, api_client, default_tenant, local_data_source):
        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A", tenant=default_tenant)
        resp = api_client.get(reverse("open_v2.list_department_children", kwargs={"lookup_value": dept_a.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert {d["name"] for d in resp.data} == {"中心AA", "中心AB"}

    def test_with_invalid_dept_id(self, api_client):
        resp = api_client.get(reverse("open_v2.list_department_children", kwargs={"lookup_value": "404"}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestListProfileDepartments:
    @pytest.fixture()
    def user_lushi(self, default_tenant, local_data_source) -> TenantUser:
        return TenantUser.objects.get(
            tenant=default_tenant,
            data_source_id=local_data_source.id,
            data_source_user__username="lushi",
        )

    def test_list_by_username(self, api_client, user_lushi):
        """通过 username (TenantUser.id) 指定用户"""
        resp = api_client.get(
            reverse(
                "open_v2.list_profile_departments",
                kwargs={"lookup_value": user_lushi.id},
            ),
            data={"lookup_field": "username", "with_ancestors": True},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert {d["full_name"] for d in resp.data} == {"公司/部门A/中心AB/小组ABA", "公司/部门B/中心BA"}
        assert "family" in resp.data[0]
        assert {d["full_name"] for d in resp.data[0]["family"]} == {"公司", "公司/部门A", "公司/部门A/中心AB"}

    def test_list_by_user_id(self, api_client, user_lushi):
        """通过 user_id (TenantUser.DataSourceUser.id) 指定用户"""
        resp = api_client.get(
            reverse(
                "open_v2.list_profile_departments",
                kwargs={"lookup_value": user_lushi.data_source_user.id},
            ),
            data={"lookup_field": "id"},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert {d["full_name"] for d in resp.data} == {"公司/部门A/中心AB/小组ABA", "公司/部门B/中心BA"}
        assert "family" not in resp.data[0]

    def test_list_with_invalid_user(self, api_client):
        """用户不存在的情况"""
        resp = api_client.get(
            reverse("open_v2.list_profile_departments", kwargs={"lookup_value": "404"}),
            data={"lookup_field": "id"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
