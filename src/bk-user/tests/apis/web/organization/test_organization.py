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
from bkuser.apps.data_source.models import DataSourceDepartment
from bkuser.apps.tenant.models import TenantDepartment
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestTenantListApi:
    def test_list(self, api_client, full_data_source):
        resp = api_client.get(reverse("organization.tenant.list"))

        tenants = resp.data
        assert len(tenants) == 1

        default_tenant = tenants[0]
        assert default_tenant["id"] == "default"
        assert default_tenant["departments"][0]["name"] == "公司"

    # TODO 补充存在协同租户的情况


class TestTenantUserListApi:
    def test_list(self, api_client, random_tenant, full_data_source):
        resp = api_client.get(
            reverse("organization.tenant.users.list", kwargs={"id": random_tenant.id}),
            data={"page": 1, "page_size": 50},
        )
        # 默认租户至少拥有 admin + 数据源同步的用户 * 11
        assert resp.data["count"] >= 12  # noqa: PLR2004
        # 由于可能存在随机用户，因此采用 subset 的方式判断是否符合预期
        tenant_usernames = {u["username"] for u in resp.data["results"]}
        must_exists_usernames = {
            "admin",
            "zhangsan",
            "lisi",
            "wangwu",
            "zhaoliu",
            "liuqi",
            "maiba",
            "yangjiu",
            "lushi",
            "linshiyi",
            "baishier",
            "freedom",
        }
        assert must_exists_usernames.issubset(tenant_usernames)


class TestTenantDepartmentChildrenListApi:
    def test_list(self, api_client, full_data_source):
        data_source_dept = DataSourceDepartment.objects.get(data_source=full_data_source, code="company")
        tenant_dept = TenantDepartment.objects.get(data_source_department=data_source_dept)
        resp = api_client.get(reverse("organization.children.list", kwargs={"id": tenant_dept.id}))

        assert {d["name"] for d in resp.data} == {"部门A", "部门B"}
        assert all(d["has_children"] for d in resp.data)

    def test_list_sub_dept_not_has_children(self, api_client, full_data_source):
        data_source_dept = DataSourceDepartment.objects.get(data_source=full_data_source, code="center_aa")
        tenant_dept = TenantDepartment.objects.get(data_source_department=data_source_dept)
        resp = api_client.get(reverse("organization.children.list", kwargs={"id": tenant_dept.id}))

        assert {d["name"] for d in resp.data} == {"小组AAA"}
        assert not any(d["has_children"] for d in resp.data)

    def test_list_not_children_dept(self, api_client, full_data_source):
        data_source_dept = DataSourceDepartment.objects.get(data_source=full_data_source, code="group_aaa")
        tenant_dept = TenantDepartment.objects.get(data_source_department=data_source_dept)
        resp = api_client.get(reverse("organization.children.list", kwargs={"id": tenant_dept.id}))
        assert resp.data == []


class TestTenantDepartmentUserListApi:
    def test_list(self, api_client, full_data_source):
        dept = TenantDepartment.objects.select_related("data_source_department").get(
            data_source=full_data_source, data_source_department__code="company"
        )
        resp = api_client.get(reverse("departments.users.list", kwargs={"id": dept.id}))

        assert resp.data["count"] == 1
        user = resp.data["results"][0]
        assert len(user["id"]) == 32  # noqa: PLR2004
        assert user["username"] == "zhangsan"
        assert user["full_name"] == "张三"
        assert user["email"] == "zhangsan@m.com"
        assert user["phone"] == "13512345671"
        assert user["departments"] == [{"id": dept.id, "name": dept.data_source_department.name}]

    def test_list_with_recursive(self, api_client, full_data_source):
        dept = TenantDepartment.objects.select_related("data_source_department").get(
            data_source=full_data_source, data_source_department__code="company"
        )
        resp = api_client.get(reverse("departments.users.list", kwargs={"id": dept.id}), data={"recursive": True})

        assert resp.data["count"] == 10  # noqa: PLR2004

    def test_list_with_recursive_and_keyword(self, api_client, full_data_source):
        dept = TenantDepartment.objects.select_related("data_source_department").get(
            data_source=full_data_source, data_source_department__code="company"
        )
        resp = api_client.get(
            reverse("departments.users.list", kwargs={"id": dept.id}), data={"recursive": True, "keyword": "lushi"}
        )

        assert resp.data["count"] == 1
        user = resp.data["results"][0]
        assert user["username"] == "lushi"
        assert {dept["name"] for dept in user["departments"]} == {"小组ABA", "中心BA"}
