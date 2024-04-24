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
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestTenantUserSearchApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_single_tenant(self, api_client, random_tenant):
        resp = api_client.get(reverse("organization.tenant_user.search"), data={"keyword": "iu"})

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 3  # noqa: PLR2004  magic number here is ok

        assert {u["username"] for u in resp.data} == {"zhaoliu", "liuqi", "yangjiu"}
        assert {u["full_name"] for u in resp.data} == {"赵六", "柳七", "杨九"}
        assert all(u["tenant_id"] == random_tenant.id for u in resp.data)
        assert all(u["status"] == "enabled" for u in resp.data)
        assert {p for u in resp.data for p in u["organization_paths"]} == {
            "公司/部门A/中心AA",
            "公司/部门A/中心AA/小组AAA",
            "公司/部门A/中心AB",
        }

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    @pytest.mark.usefixtures("_init_collaborative_users_depts")
    def test_multi_tenant(self, api_client, random_tenant, collaborative_tenant):
        resp = api_client.get(reverse("organization.tenant_user.search"), data={"keyword": "hi"})

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 6  # noqa: PLR2004  magic number here is ok

        assert {u["username"] for u in resp.data} == {"lushi", "linshiyi", "baishier"}
        assert {u["tenant_id"] for u in resp.data} == {random_tenant.id, collaborative_tenant.id}
        assert {p for u in resp.data for p in u["organization_paths"]} == {
            "公司/部门A/中心AB/小组ABA",
            "公司/部门B/中心BA",
            "公司/部门B/中心BA/小组BAA",
        }

    def test_match_nothing(self, api_client):
        resp = api_client.get(reverse("organization.tenant_department.search"), data={"keyword": "2887"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0
