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

pytestmark = pytest.mark.django_db


class TestTenantDepartmentUserListApi:
    def test_list(self, api_client, full_data_source):
        dept = TenantDepartment.objects.select_related("data_source_department").get(
            data_source=full_data_source, data_source_department__code="company"
        )
        resp = api_client.get(reverse("departments.users.list", args=[dept.id]))

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
        resp = api_client.get(reverse("departments.users.list", args=[dept.id]), data={"recursive": True})

        assert resp.data["count"] == 10  # noqa: PLR2004

    def test_list_with_recursive_and_keyword(self, api_client, full_data_source):
        dept = TenantDepartment.objects.select_related("data_source_department").get(
            data_source=full_data_source, data_source_department__code="company"
        )
        resp = api_client.get(
            reverse("departments.users.list", args=[dept.id]), data={"recursive": True, "keyword": "lushi"}
        )

        assert resp.data["count"] == 1
        user = resp.data["results"][0]
        assert user["username"] == "lushi"
        assert {dept["name"] for dept in user["departments"]} == {"小组ABA", "中心BA"}


class TestTenantListApi:
    def test_list(self, api_client, full_data_source):
        resp = api_client.get(reverse("organization.tenant.list"))

        tenants = resp.data
        assert len(tenants) == 1

        default_tenant = tenants[0]
        assert default_tenant["id"] == "default"
        assert default_tenant["departments"][0]["name"] == "公司"

        # TODO 补充存在协同租户的情况


class TestTenantDepartmentChildrenListApi:
    pass


class TestTenantUserListApi:
    pass
