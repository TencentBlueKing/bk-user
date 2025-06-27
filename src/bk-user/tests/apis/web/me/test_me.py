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
from bkuser.apps.tenant.models import TenantUser, VirtualUserAppRelation, VirtualUserOwnerRelation
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestMeVirtualUserListApi:
    @pytest.mark.usefixtures("_init_virtual_users")
    def test_list_virtual_user(self, api_client):
        resp = api_client.get(reverse("me.virtual_users.list"))
        assert resp.status_code == status.HTTP_200_OK
        assert set(resp.data["results"][0].keys()) == {
            "id",
            "username",
            "full_name",
            "app_codes",
            "owners",
            "created_at",
        }

    @pytest.mark.usefixtures("_init_virtual_users")
    def test_list_virtual_user_with_pagination(self, api_client):
        resp = api_client.get(reverse("me.virtual_users.list"), data={"page": 1, "page_size": 2})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 2
        assert resp.data["count"] == 3

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_list_virtual_user_empty(self, api_client):
        resp = api_client.get(reverse("me.virtual_users.list"))
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 0
        assert resp.data["count"] == 0

    @pytest.mark.usefixtures("_init_virtual_users")
    def test_list_virtual_user_with_keyword(self, api_client):
        # 测试能匹配当前用户负责的所有虚拟用户
        resp = api_client.get(reverse("me.virtual_users.list"), data={"keyword": "virtual"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 3
        assert {r["id"] for r in resp.data["results"]} == {"virtual_user_1", "virtual_user_3", "virtual_user_4"}

        # 测试只匹配 virtual_user_1
        resp = api_client.get(reverse("me.virtual_users.list"), data={"keyword": "virtual_user_1"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 1
        assert resp.data["results"][0]["id"] == "virtual_user_1"

        # 测试不匹配情况
        resp = api_client.get(reverse("me.virtual_users.list"), data={"keyword": "virtual_user_not_exist"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 0
        assert resp.data["count"] == 0


@pytest.mark.usefixtures("_init_virtual_users")
class TestMeVirtualUserGetApi:
    def test_get_virtual_user(self, api_client, random_tenant):
        url = reverse("me.virtual_users.retrieve_update", kwargs={"id": "virtual_user_1"})
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["username"] == "virtual_user_1"

    def test_get_virtual_user_not_owned(self, api_client):
        url = reverse("me.virtual_users.retrieve_update", kwargs={"id": "virtual_user_2"})
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_get_virtual_user_not_exists(self, api_client):
        url = reverse("me.virtual_users.retrieve_update", kwargs={"id": "virtual_user_not_exist"})
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("_init_virtual_users")
class TestMeVirtualUserUpdateApi:
    def test_update_virtual_user(self, api_client):
        url = reverse("me.virtual_users.retrieve_update", kwargs={"id": "virtual_user_1"})
        resp = api_client.put(
            url,
            data={"full_name": "虚拟用户的新名字", "app_codes": ["app4", "app5"], "owners": ["zhangsan", "wangwu"]},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        virtual_user = TenantUser.objects.get(id="virtual_user_1")
        assert virtual_user.data_source_user.full_name == "虚拟用户的新名字"
        assert set(
            VirtualUserAppRelation.objects.filter(tenant_user=virtual_user).values_list("app_code", flat=True)
        ) == {"app4", "app5"}
        assert set(
            VirtualUserOwnerRelation.objects.filter(tenant_user=virtual_user).values_list("owner", flat=True)
        ) == {"zhangsan", "wangwu"}

    def test_update_virtual_user_not_owned(self, api_client):
        url = reverse("me.virtual_users.retrieve_update", kwargs={"id": "virtual_user_2"})
        resp = api_client.put(
            url,
            data={"full_name": "虚拟用户的新名字", "app_codes": ["app4", "app5"], "owners": ["zhangsan", "wangwu"]},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_update_virtual_user_not_exists(self, api_client):
        url = reverse("me.virtual_users.retrieve_update", kwargs={"id": "virtual_user_not_exist"})
        resp = api_client.put(
            url,
            data={"full_name": "虚拟用户的新名字", "app_codes": ["app4", "app5"], "owners": ["zhangsan", "wangwu"]},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.usefixtures("_init_cross_tenant_user")
    def test_update_virtual_user_with_owner_cross_tenant(self, api_client):
        url = reverse("me.virtual_users.retrieve_update", kwargs={"id": "virtual_user_1"})
        assert TenantUser.objects.filter(id="cross_tenant_user").exists()
        resp = api_client.put(
            url,
            data={
                "full_name": "虚拟用户的新名字",
                "app_codes": ["app4", "app5"],
                "owners": ["zhangsan", "wangwu", "cross_tenant_user"],
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "用户 {'cross_tenant_user'} 不存在、不是实体用户或不属于当前租户" in resp.data["message"]
