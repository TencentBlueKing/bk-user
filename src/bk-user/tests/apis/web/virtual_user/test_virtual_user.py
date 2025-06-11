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
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.models import TenantUser, VirtualUserAppRelation, VirtualUserOwnerRelation
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_virtual_users")
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
    @pytest.mark.usefixtures("_init_virtual_users")
    def test_list_virtual_user(self, api_client):
        virtual_user_1 = TenantUser.objects.get(
            data_source_user__username="virtual_user_1", data_source__type=DataSourceTypeEnum.VIRTUAL
        )
        virtual_user_2 = TenantUser.objects.get(
            data_source_user__username="virtual_user_2", data_source__type=DataSourceTypeEnum.VIRTUAL
        )
        virtual_user_3 = TenantUser.objects.get(
            data_source_user__username="virtual_user_3", data_source__type=DataSourceTypeEnum.VIRTUAL
        )

        resp = api_client.get(reverse("virtual_user.list_create"))
        assert resp.status_code == status.HTTP_200_OK

        assert resp.data["count"] == 3
        results = resp.data["results"]
        assert {item["username"] for item in results} == {
            virtual_user_1.data_source_user.username,
            virtual_user_2.data_source_user.username,
            virtual_user_3.data_source_user.username,
        }
        assert {item["full_name"] for item in results} == {
            virtual_user_1.data_source_user.full_name,
            virtual_user_2.data_source_user.full_name,
            virtual_user_3.data_source_user.full_name,
        }

        user_data_map = {item["username"]: item for item in results}
        assert set(user_data_map["virtual_user_1"]["app_codes"]) == {"app1", "app2"}
        assert set(user_data_map["virtual_user_1"]["owners"]) == {"zhangsan", "lisi"}
        assert set(user_data_map["virtual_user_2"]["app_codes"]) == {"app3"}
        assert set(user_data_map["virtual_user_2"]["owners"]) == {"lisi", "wangwu", "zhaoliu", "liuqi"}
        assert set(user_data_map["virtual_user_3"]["app_codes"]) == {"app4", "app5"}
        assert set(user_data_map["virtual_user_3"]["owners"]) == {"maiba", "yangjiu", "lushi"}

    @pytest.mark.usefixtures("_init_virtual_users")
    def test_list_virtual_user_with_pagination(self, api_client):
        virtual_user_1 = TenantUser.objects.get(
            data_source_user__username="virtual_user_1", data_source__type=DataSourceTypeEnum.VIRTUAL
        )
        virtual_user_2 = TenantUser.objects.get(
            data_source_user__username="virtual_user_2", data_source__type=DataSourceTypeEnum.VIRTUAL
        )

        resp = api_client.get(reverse("virtual_user.list_create"), data={"page": 1, "page_size": 2})

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 3
        assert len(resp.data["results"]) == 2
        results = resp.data["results"]
        assert {t["username"] for t in results} == {
            virtual_user_1.data_source_user.username,
            virtual_user_2.data_source_user.username,
        }
        assert {t["full_name"] for t in results} == {
            virtual_user_1.data_source_user.full_name,
            virtual_user_2.data_source_user.full_name,
        }

        user_data_map = {item["username"]: item for item in results}
        assert set(user_data_map["virtual_user_1"]["app_codes"]) == {"app1", "app2"}
        assert set(user_data_map["virtual_user_1"]["owners"]) == {"zhangsan", "lisi"}
        assert set(user_data_map["virtual_user_2"]["app_codes"]) == {"app3"}
        assert set(user_data_map["virtual_user_2"]["owners"]) == {"lisi", "wangwu", "zhaoliu", "liuqi"}

    def test_list_virtual_user_empty(self, api_client):
        resp = api_client.get(reverse("virtual_user.list_create"))
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 0

    @pytest.mark.usefixtures("_init_virtual_users")
    def test_list_virtual_user_with_keyword(self, api_client):
        virtual_user_1 = TenantUser.objects.get(
            data_source_user__username="virtual_user_1", data_source__type=DataSourceTypeEnum.VIRTUAL
        )
        virtual_user_2 = TenantUser.objects.get(
            data_source_user__username="virtual_user_2", data_source__type=DataSourceTypeEnum.VIRTUAL
        )
        virtual_user_3 = TenantUser.objects.get(
            data_source_user__username="virtual_user_3", data_source__type=DataSourceTypeEnum.VIRTUAL
        )

        resp = api_client.get(reverse("virtual_user.list_create") + "?keyword=virtual")

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 3
        results = resp.data["results"]
        assert {item["username"] for item in results} == {
            virtual_user_1.data_source_user.username,
            virtual_user_2.data_source_user.username,
            virtual_user_3.data_source_user.username,
        }
        assert {item["full_name"] for item in results} == {
            virtual_user_1.data_source_user.full_name,
            virtual_user_2.data_source_user.full_name,
            virtual_user_3.data_source_user.full_name,
        }
        user_data_map = {item["username"]: item for item in results}
        assert set(user_data_map["virtual_user_1"]["app_codes"]) == {"app1", "app2"}
        assert set(user_data_map["virtual_user_1"]["owners"]) == {"zhangsan", "lisi"}
        assert set(user_data_map["virtual_user_2"]["app_codes"]) == {"app3"}
        assert set(user_data_map["virtual_user_2"]["owners"]) == {"lisi", "wangwu", "zhaoliu", "liuqi"}
        assert set(user_data_map["virtual_user_3"]["app_codes"]) == {"app4", "app5"}
        assert set(user_data_map["virtual_user_3"]["owners"]) == {"maiba", "yangjiu", "lushi"}

        # 测试只匹配 virtual_user_1
        resp = api_client.get(reverse("virtual_user.list_create") + "?keyword=virtual_user_1")
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data["results"]
        assert len(results) == 1
        assert results[0]["username"] == "virtual_user_1"
        assert results[0]["full_name"] == "虚拟用户1"
        assert set(results[0]["app_codes"]) == {"app1", "app2"}
        assert set(results[0]["owners"]) == {"zhangsan", "lisi"}

        # 测试不匹配情况
        resp = api_client.get(reverse("virtual_user.list_create") + "?keyword=not_exist")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 0
        assert len(resp.data["results"]) == 0


@pytest.mark.usefixtures("_init_virtual_users")
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

        url = reverse("virtual_user.retrieve_update_destroy", kwargs={"id": virtual_user.id})
        resp = api_client.get(url)

        assert resp.status_code == status.HTTP_200_OK

        assert resp.data["username"] == data_source_user.username
        assert resp.data["full_name"] == data_source_user.full_name
        assert set(resp.data["app_codes"]) == set(app_codes)
        assert set(resp.data["owners"]) == set(owners)

    def test_get_virtual_user_not_exists(self, api_client):
        url = reverse("virtual_user.retrieve_update_destroy", kwargs={"id": "virtual_user_not_exists"})
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("_init_virtual_users")
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


@pytest.mark.usefixtures("_init_virtual_users")
class TestVirtualDeleteApi:
    def test_delete_virtual_user(self, api_client):
        url = reverse("virtual_user.retrieve_update_destroy", kwargs={"id": "virtual_user_1"})

        resp = api_client.delete(url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        assert not TenantUser.objects.filter(id="virtual_user_1").exists()
        assert not DataSourceUser.objects.filter(username="virtual_user_1").exists()
        assert not VirtualUserAppRelation.objects.filter(tenant_user_id="virtual_user_1").exists()
        assert not VirtualUserOwnerRelation.objects.filter(tenant_user_id="virtual_user_1").exists()

        assert TenantUser.objects.filter(id="virtual_user_2").exists()
        assert TenantUser.objects.filter(id="virtual_user_3").exists()
