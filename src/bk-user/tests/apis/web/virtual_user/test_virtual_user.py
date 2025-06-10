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
    @pytest.mark.parametrize(
        "user_data",
        [
            pytest.param(
                {
                    "username": "virtual_user_4",
                    "full_name": "测试用户4",
                    "app_codes": ["app1", "app2"],
                    "owners": ["owner1", "owner2"],
                },
                id="virtual_user_4",
            ),
            pytest.param(
                {
                    "username": "virtual_user_5",
                    "full_name": "测试用户5",
                    "app_codes": ["app3"],
                    "owners": ["owner3"],
                },
                id="virtual_user_5",
            ),
            pytest.param(
                {
                    "username": "virtual_user_6",
                    "full_name": "测试用户6",
                    "app_codes": ["app1", "app3", "app4"],
                    "owners": ["owner1", "owner4"],
                },
                id="virtual_user_6",
            ),
        ],
    )
    def test_create_virtual_user(self, api_client, user_data):
        url = reverse("virtual_user.list_create")
        resp = api_client.post(url, data=user_data)
        assert resp.status_code == status.HTTP_201_CREATED
        data_source_user = DataSourceUser.objects.get(username=user_data["username"])
        tenant_user = TenantUser.objects.get(data_source_user=data_source_user)
        assert resp.data["id"] == tenant_user.id
        assert DataSourceUser.objects.filter(username=user_data["username"]).exists()

    @pytest.mark.parametrize(
        "user_data",
        [
            pytest.param(
                {
                    "username": "invalid_user_1",
                    "full_name": "无效用户1",
                    "app_codes": ["app1"],
                    "owners": ["invalid_owner1"],
                },
                id="invalid_owner_case1",
            ),
            pytest.param(
                {
                    "username": "invalid_user_2",
                    "full_name": "无效用户2",
                    "app_codes": ["app2", "app3"],
                    "owners": ["invalid_owner2", "owner1"],
                },
                id="invalid_owner_case2",
            ),
            pytest.param(
                {
                    "username": "invalid_user_3",
                    "full_name": "无效用户3",
                    "app_codes": ["app4"],
                    "owners": ["invalid_owner3", "owner1", "owner2"],
                },
                id="empty_owner_case",
            ),
        ],
    )
    def test_create_virtual_user_invalid_owner(self, api_client, user_data):
        resp = api_client.post(reverse("virtual_user.list_create"), data=user_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不存在或不是实体用户" in resp.data["message"]


class TestVirtualUserListApi:
    @pytest.mark.usefixtures("_init_virtual_user")
    def test_list_virtual_user(self, api_client, virtual_user_data):
        expected_usernames = {user["username"] for user in virtual_user_data["users"]}
        expected_app_codes = {user["username"]: set(user["app_codes"]) for user in virtual_user_data["users"]}
        expected_owners = {user["username"]: set(user["owners"]) for user in virtual_user_data["users"]}

        resp = api_client.get(reverse("virtual_user.list_create"))
        assert resp.status_code == status.HTTP_200_OK

        results = resp.data["results"]
        result_usernames = {item["username"] for item in results}
        result_app_codes = {item["username"]: set(item["app_codes"]) for item in results}
        result_owners = {item["username"]: set(item["owners"]) for item in results}

        assert result_usernames == expected_usernames

        for username in expected_usernames:
            assert result_app_codes.get(username) == expected_app_codes.get(username)
            assert result_owners.get(username) == expected_owners.get(username)

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
        assert "other_user" not in usernames


@pytest.mark.usefixtures("_init_virtual_user")
class TestVirtualUserGetApi:
    @pytest.mark.parametrize("user_index", [0, 1, 2])
    def test_get_virtual_user(self, api_client, virtual_user_data, user_index):
        # 使用第一个预置用户进行测试
        test_user_data = virtual_user_data["users"][user_index]

        url = reverse("virtual_user.retrieve_update_destroy", kwargs={"id": test_user_data["tenant_user_id"]})
        resp = api_client.get(url)

        assert resp.status_code == status.HTTP_200_OK

        assert resp.data["username"] == test_user_data["username"]
        assert resp.data["full_name"] == test_user_data["full_name"]
        assert set(resp.data["app_codes"]) == set(test_user_data["app_codes"])
        assert set(resp.data["owners"]) == set(test_user_data["owners"])

    def test_get_virtual_user_not_found(self, api_client):
        url = reverse("virtual_user.retrieve_update_destroy", kwargs={"id": "not_found"})
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("_init_virtual_user")
class TestVirtualUserUpdateApi:
    def _prepare_update_request(self, virtual_user_data, update_fields, user_index=0):
        """准备更新请求的数据"""
        test_user_data = virtual_user_data["users"][user_index]
        virtual_user = TenantUser.objects.get(id=test_user_data["tenant_user_id"])

        url = reverse("virtual_user.retrieve_update_destroy", kwargs={"id": virtual_user.id})
        request_data = {
            "full_name": virtual_user.data_source_user.full_name,
            "app_codes": list(virtual_user.virtualuserapprelation_set.values_list("app_code", flat=True)),
            "owners": [rel.owner_id for rel in virtual_user.virtualuserownerrelation_set.all()],
        }
        request_data.update(update_fields)
        return url, request_data, virtual_user

    @pytest.mark.parametrize(
        "update_fields",
        [
            pytest.param(
                {"full_name": "更新后的名字"},
            ),
            pytest.param(
                {"app_codes": ["new_app1", "new_app2"]},
            ),
            pytest.param(
                {"owners": ["owner5", "owner6"]},
            ),
            pytest.param(
                {"full_name": "更新后的名字", "app_codes": ["new_app1", "new_app2"], "owners": ["owner5", "owner6"]},
            ),
        ],
    )
    def test_update_virtual_user(self, api_client, update_fields, virtual_user_data):
        # 使用第一个预置用户进行测试
        url, request_data, virtual_user = self._prepare_update_request(virtual_user_data, update_fields)
        test_data = virtual_user_data["users"][0]

        resp = api_client.put(
            url,
            data=request_data,
            format="json",
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        virtual_user.refresh_from_db()

        # 验证全名更新
        expected_full_name = update_fields.get("full_name", test_data["full_name"])
        assert virtual_user.data_source_user.full_name == expected_full_name

        # 验证应用关联更新
        expected_app_codes = set(update_fields.get("app_codes", test_data["app_codes"]))
        actual_app_codes = set(virtual_user.virtualuserapprelation_set.values_list("app_code", flat=True))
        assert actual_app_codes == expected_app_codes

        # 验证责任人关联更新
        expected_owners = set(update_fields.get("owners", test_data["owners"]))
        actual_owners = {rel.owner_id for rel in virtual_user.virtualuserownerrelation_set.all()}
        assert actual_owners == expected_owners

    @pytest.mark.parametrize(
        "update_fields",
        [
            pytest.param(
                {"owners": ["invalid_owner1", "owner6"]},
            ),
        ],
    )
    def test_update_virtual_user_with_invalid_owner(self, api_client, update_fields, virtual_user_data):
        url, request_data, virtual_user = self._prepare_update_request(virtual_user_data, update_fields)
        resp = api_client.put(
            url,
            data=request_data,
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不存在或不是实体用户" in resp.data["message"]


@pytest.mark.usefixtures("_init_virtual_user")
class TestVirtualDeleteApi:
    @pytest.mark.parametrize("user_index", [0, 1, 2])
    def test_delete_virtual_user_with_prepared_data(self, api_client, virtual_user_data, user_index):
        test_user_data = virtual_user_data["users"][user_index]
        tenant_user = TenantUser.objects.get(id=test_user_data["tenant_user_id"])
        data_source_user = tenant_user.data_source_user

        url = reverse("virtual_user.retrieve_update_destroy", kwargs={"id": test_user_data["tenant_user_id"]})
        resp = api_client.delete(url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        # 验证主对象是否被删除
        with pytest.raises(TenantUser.DoesNotExist):
            TenantUser.objects.get(id=test_user_data["tenant_user_id"])

        # 验证数据源用户也被删除
        with pytest.raises(DataSourceUser.DoesNotExist):
            DataSourceUser.objects.get(id=data_source_user.id)

        # 验证关联表也清理干净
        assert not VirtualUserAppRelation.objects.filter(tenant_user=test_user_data["tenant_user_id"]).exists()
        assert not VirtualUserOwnerRelation.objects.filter(tenant_user=test_user_data["tenant_user_id"]).exists()
