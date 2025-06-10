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
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.models import TenantUser, VirtualUserAppRelation, VirtualUserOwnerRelation
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_virtual_user")
class TestVirtualUserCreateApi:
    def test_create_virtual_user(self, api_client):
        data = {
            "username": "virtual_user_4",
            "full_name": "测试用户4",
            "app_codes": ["app1", "app2", "app3"],
            "owners": ["lisi", "wangwu"],
        }

        url = reverse("virtual_user.list_create")
        resp = api_client.post(url, data=data)
        assert resp.status_code == status.HTTP_201_CREATED
        data_source_user = DataSourceUser.objects.get(username=data["username"])
        tenant_user = TenantUser.objects.get(data_source_user=data_source_user)
        assert resp.data["id"] == tenant_user.id
        assert DataSourceUser.objects.filter(username=data["username"]).exists()

    @pytest.mark.parametrize(
        "user_data",
        [
            {
                "username": "virtual_user_4",
                "full_name": "测试用户4",
                "app_codes": ["app1"],
                "owners": ["zhangwei"],
            },
            {
                "username": "virtual_user_5",
                "full_name": "测试用户5",
                "app_codes": ["app2", "app3"],
                "owners": ["zhangsan", "zhangwei", "lisi"],
            },
            {
                "username": "virtual_user_6",
                "full_name": "测试用户6",
                "app_codes": ["app4"],
                "owners": ["wangwu", "zhaoliu", "zhangwei"],
            },
        ],
    )
    def test_create_virtual_user_invalid_owner(self, api_client, user_data):
        resp = api_client.post(reverse("virtual_user.list_create"), data=user_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "用户 {'zhangwei'} 不存在或不是实体用户" in resp.data["message"]


class TestVirtualUserListApi:
    @pytest.mark.usefixtures("_init_virtual_user")
    def test_list_virtual_user(self, api_client):
        expected_data = {
            "virtual_user_1": {
                "full_name": "虚拟用户1",
                "app_codes": {"app1", "app2"},
                "owners": {"zhangsan", "lisi"},
            },
            "virtual_user_2": {
                "full_name": "虚拟用户2",
                "app_codes": {"app3"},
                "owners": {"lisi", "wangwu", "zhaoliu", "liuqi"},
            },
            "virtual_user_3": {
                "full_name": "虚拟用户3",
                "app_codes": {"app4", "app5"},
                "owners": {"maiba", "yangjiu", "lushi"},
            },
        }

        resp = api_client.get(reverse("virtual_user.list_create"))
        assert resp.status_code == status.HTTP_200_OK

        results = resp.data["results"]
        assert len(results) == len(expected_data)
        for item in results:
            username = item["username"]
            expected = expected_data[username]
            assert item["full_name"] == expected["full_name"]
            assert set(item["app_codes"]) == set(expected["app_codes"])
            assert set(item["owners"]) == set(expected["owners"])

    def test_list_virtual_user_empty(self, api_client):
        resp = api_client.get(reverse("virtual_user.list_create"))
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 0

    @pytest.mark.usefixtures("_init_virtual_user")
    def test_list_virtual_user_with_keyword(self, api_client):
        resp = api_client.get(reverse("virtual_user.list_create") + "?keyword=virtual")
        assert resp.status_code == status.HTTP_200_OK
        usernames = {item["username"] for item in resp.data["results"]}
        assert {"virtual_user_1", "virtual_user_2", "virtual_user_3"} == usernames

        resp = api_client.get(reverse("virtual_user.list_create") + "?keyword=virtual_user_1")
        assert resp.status_code == status.HTTP_200_OK
        usernames = {item["username"] for item in resp.data["results"]}
        assert {"virtual_user_1"} == usernames
        assert {"virtual_user_2", "virtual_user_3"} not in usernames


@pytest.mark.usefixtures("_init_virtual_user")
class TestVirtualUserGetApi:
    def test_get_virtual_user(self, api_client):
        virtual_user = TenantUser.objects.get(id="virtual_user_2")
        data_source_user = virtual_user.data_source_user
        app_codes = list(
            VirtualUserAppRelation.objects.filter(tenant_user=virtual_user).values_list("app_code", flat=True)
        )
        owners = list(
            VirtualUserOwnerRelation.objects.filter(tenant_user=virtual_user).values_list("owner", flat=True)
        )

        url = reverse("virtual_user.retrieve_update_destroy", kwargs={"id": "virtual_user_2"})
        resp = api_client.get(url)

        assert resp.status_code == status.HTTP_200_OK

        assert resp.data["username"] == data_source_user.username
        assert resp.data["full_name"] == data_source_user.full_name
        assert set(resp.data["app_codes"]) == set(app_codes)
        assert set(resp.data["owners"]) == set(owners)

    def test_get_virtual_user_not_exists(self, api_client):
        url = reverse("virtual_user.retrieve_update_destroy", kwargs={"id": "virtual_user_4"})
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("_init_virtual_user")
class TestVirtualUserUpdateApi:
    def test_update_virtual_user(self, api_client):
        url = reverse("virtual_user.retrieve_update_destroy", kwargs={"id": "virtual_user_1"})
        resp = api_client.put(
            url,
            data={"full_name": "测试虚拟用户", "app_codes": ["app3", "app4"], "owners": ["freedom", "lushi"]},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        virtual_user = TenantUser.objects.get(id="virtual_user_1")

        assert virtual_user.data_source_user.full_name == "测试虚拟用户"
        assert set(virtual_user.virtualuserapprelation_set.values_list("app_code", flat=True)) == {"app3", "app4"}
        assert set(virtual_user.virtualuserownerrelation_set.values_list("owner_id", flat=True)) == {
            "freedom",
            "lushi",
        }

    def test_update_virtual_user_with_invalid_owner(self, api_client):
        url = reverse("virtual_user.retrieve_update_destroy", kwargs={"id": "virtual_user_1"})
        resp = api_client.put(
            url,
            data={
                "full_name": "测试虚拟用户",
                "app_codes": ["app3", "app4"],
                "owners": ["freedom", "lushi", "zhangwei"],
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "用户 {'zhangwei'} 不存在或不是实体用户" in resp.data["message"]


@pytest.mark.usefixtures("_init_virtual_user")
class TestVirtualDeleteApi:
    def test_delete_virtual_user(self, api_client):
        url = reverse("virtual_user.retrieve_update_destroy", kwargs={"id": "virtual_user_1"})

        # 确保用户存在
        assert TenantUser.objects.filter(id="virtual_user_1").exists()
        assert DataSourceUser.objects.filter(username="virtual_user_1").exists()
        # 执行删除操作
        resp = api_client.delete(url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        # 验证用户及相关数据已被删除
        assert not TenantUser.objects.filter(id="virtual_user_1").exists()
        assert not DataSourceUser.objects.filter(username="virtual_user_1").exists()
        assert not VirtualUserAppRelation.objects.filter(tenant_user_id="virtual_user_1").exists()
        assert not VirtualUserOwnerRelation.objects.filter(tenant_user_id="virtual_user_1").exists()
        # 验证其他虚拟用户没有被误删
        assert TenantUser.objects.filter(id="virtual_user_2").exists()
        assert TenantUser.objects.filter(id="virtual_user_3").exists()
