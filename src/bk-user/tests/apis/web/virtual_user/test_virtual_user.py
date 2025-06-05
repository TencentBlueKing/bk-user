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
from typing import Callable

import pytest
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.models import Tenant, TenantUser, VirtualUserAppRelation, VirtualUserOwnerRelation
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def _create_owners_for_test(create_real_owner: Callable, tenant: Tenant, owners: list[str]):
    for owner in owners:
        create_real_owner(tenant, owner)


class TestVirtualUserCreateApi:
    def test_create_virtual_user_success(self, api_client, valid_data, create_real_owner, random_tenant):
        _create_owners_for_test(create_real_owner, random_tenant, valid_data["owners"])
        url = reverse("virtual_user.list_create")
        resp = api_client.post(
            url,
            data=valid_data,
        )
        assert resp.status_code == status.HTTP_201_CREATED
        data_source_user = DataSourceUser.objects.get(username=valid_data["username"])
        tenant_user = TenantUser.objects.get(data_source_user=data_source_user)
        assert resp.data["id"] == tenant_user.id
        assert DataSourceUser.objects.filter(username=valid_data["username"]).exists()

    def test_create_virtual_user_duplicate_username(self, api_client, valid_data, create_real_owner, random_tenant):
        _create_owners_for_test(create_real_owner, random_tenant, valid_data["owners"])
        url = reverse("virtual_user.list_create")
        resp = api_client.post(url, data=valid_data)
        assert resp.status_code == status.HTTP_201_CREATED

        # 第二次创建应失败
        resp = api_client.post(url, data=valid_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert f"用户名 {valid_data['username']} 已存在" in resp.data["message"]

    def test_create_virtual_user_invalid_owner(self, api_client, valid_data, create_real_owner, random_tenant):
        _create_owners_for_test(create_real_owner, random_tenant, valid_data["owners"])
        data = valid_data.copy()
        data["owners"] = ["invalid_owner"]
        resp = api_client.post(reverse("virtual_user.list_create"), data=data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "用户 invalid_owner 不存在" in resp.data["message"]

    def test_create_virtual_user_duplicate_app_codes(self, api_client, valid_data, create_real_owner, random_tenant):
        data = valid_data.copy()
        data["app_codes"] = ["app_code_1", "app_code_1", "app_code_2"]
        _create_owners_for_test(create_real_owner, random_tenant, data["owners"])
        resp = api_client.post(reverse("virtual_user.list_create"), data=data)
        assert resp.status_code == status.HTTP_201_CREATED

        # 获取创建的租户用户
        tenant_user = TenantUser.objects.get(id=resp.data["id"])
        # 验证实际存储的 app_code 已去重
        assert list(tenant_user.virtualuserapprelation_set.all().values_list("app_code", flat=True)) == [
            "app_code_1",
            "app_code_2",
        ]

    def test_create_virtual_user_relations(self, api_client, valid_data, create_real_owner, random_tenant):
        _create_owners_for_test(create_real_owner, random_tenant, valid_data["owners"])
        resp = api_client.post(reverse("virtual_user.list_create"), data=valid_data)
        assert resp.status_code == status.HTTP_201_CREATED

        tenant_user = TenantUser.objects.get(id=resp.data["id"])
        # 验证应用关联
        assert set(tenant_user.virtualuserapprelation_set.values_list("app_code", flat=True)) == set(
            valid_data["app_codes"]
        )
        # 验证责任人关联
        assert {rel.owner.data_source_user.username for rel in tenant_user.virtualuserownerrelation_set.all()} == set(
            valid_data["owners"]
        )


class TestVirtualUserListApi:
    @pytest.mark.parametrize(
        "users_data",
        [
            # 单个用户，带 app 和 owner
            [
                {
                    "username": "virtual_user1",
                    "full_name": "用户1",
                    "app_codes": ["app1", "app2"],
                    "owners": ["owner1", "owner2"],
                },
            ],
            # 多个用户，包含多个 app 和 owner
            [
                {
                    "username": "virtual_user1",
                    "full_name": "用户1",
                    "app_codes": ["app1", "app2"],
                    "owners": ["owner1", "owner3"],
                },
                {
                    "username": "virtual_user2",
                    "full_name": "用户2",
                    "app_codes": ["app3"],
                    "owners": ["owner2", "owner4"],
                },
            ],
        ],
    )
    def test_list_virtual_user_success(
        self, api_client, random_tenant, create_real_owner, create_virtual_user_with_relations, users_data
    ):
        all_owners = set()
        for user in users_data:
            all_owners.update(user["owners"])

        # 创建责任人
        _create_owners_for_test(create_real_owner, random_tenant, list(all_owners))

        # 创建虚拟用户
        expected_usernames = set()
        expected_app_codes = {}
        expected_owners = {}

        for data in users_data:
            username = data["username"]
            full_name = data["full_name"]
            app_codes = data["app_codes"]
            owners = data["owners"]

            create_virtual_user_with_relations(
                tenant=random_tenant,
                username=username,
                full_name=full_name,
                app_codes=app_codes,
                owners=owners,
            )

            expected_usernames.add(username)
            expected_app_codes[username] = set(app_codes)
            expected_owners[username] = set(owners)

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

    def test_list_virtual_user_empty(self, api_client, random_tenant):
        resp = api_client.get(reverse("virtual_user.list_create"))
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 0

    def test_list_virtual_user_with_keyword(self, api_client, create_virtual_user, random_tenant):
        create_virtual_user(random_tenant, "virtual_user1")
        create_virtual_user(random_tenant, "other_user2")

        resp = api_client.get(reverse("virtual_user.list_create") + "?keyword=virtual")
        assert resp.status_code == status.HTTP_200_OK
        usernames = {item["username"] for item in resp.data["results"]}
        assert "virtual_user1" in usernames
        assert "other_user" not in usernames


class TestVirtualUserGetApi:
    @pytest.mark.parametrize(
        ("username", "full_name", "app_codes", "owners"),
        [
            ("virtual_user1", "用户1", ["app1", "app2"], ["owner1", "owner2"]),
            ("test_user", "测试用户", ["app1", "app2", "app2"], ["owner1", "owner2"]),
            ("test_user_1", "测试用户1", ["app1"], ["owner1"]),
            ("test_user_2", "测试用户2", ["app2"], ["owner1", "owner2", "owner3"]),
        ],
    )
    def test_get_virtual_user_success(
        self,
        api_client,
        random_tenant,
        create_virtual_user_with_relations,
        create_real_owner,
        username,
        full_name,
        app_codes,
        owners,
    ):
        # 创建责任人
        _create_owners_for_test(create_real_owner, random_tenant, owners)
        # 创建虚拟用户
        virtual_user: TenantUser = create_virtual_user_with_relations(
            tenant=random_tenant,
            username=username,
            full_name=full_name,
            app_codes=app_codes,
            owners=owners,
        )

        url = reverse("virtual_user.retrieve_update_destroy", kwargs={"id": virtual_user.id})
        resp = api_client.get(url)

        assert resp.status_code == status.HTTP_200_OK

        assert resp.data["username"] == username
        assert resp.data["full_name"] == full_name
        assert set(resp.data["app_codes"]) == set(app_codes)
        assert set(resp.data["owners"]) == set(owners)


class TestVirtualUserUpdateApi:
    def test_update_virtual_user_success(
        self, api_client, random_tenant, create_real_owner, create_virtual_user_with_relations
    ):
        username = "original_user"
        old_full_name = "旧名字"
        new_full_name = "新名字"
        old_app_codes = ["old_app1", "old_app2"]
        new_app_codes = ["new_app1", "new_app2"]
        old_owners = ["old_owner1", "old_owner2"]
        new_owners = ["new_owner1", "new_owner2"]
        _create_owners_for_test(create_real_owner, random_tenant, owners=new_owners)
        _create_owners_for_test(create_real_owner, random_tenant, owners=old_owners)

        virtual_user: TenantUser = create_virtual_user_with_relations(
            tenant=random_tenant,
            username=username,
            full_name=old_full_name,
            app_codes=old_app_codes,
            owners=old_owners,
        )

        url = reverse("virtual_user.retrieve_update_destroy", kwargs={"id": virtual_user.id})
        update_data = {
            "full_name": new_full_name,
            "app_codes": new_app_codes,
            "owners": new_owners,
        }

        resp = api_client.put(url, data=update_data, format="json")
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        virtual_user.refresh_from_db()
        data_source_user = virtual_user.data_source_user
        assert data_source_user.full_name == new_full_name

        # 验证应用关联
        assert set(virtual_user.virtualuserapprelation_set.values_list("app_code", flat=True)) == set(new_app_codes)

        # 验证责任人关联
        assert {rel.owner.data_source_user.username for rel in virtual_user.virtualuserownerrelation_set.all()} == set(
            new_owners
        )


class TestVirtualDeleteApi:
    def test_delete_virtual_user_success(
        self, api_client, random_tenant, create_real_owner, create_virtual_user_with_relations
    ):
        username = "delete_user"
        owners = ["owner1", "owner2"]
        app_codes = ["app1", "app2"]
        _create_owners_for_test(create_real_owner, random_tenant, owners)
        virtual_user: TenantUser = create_virtual_user_with_relations(
            tenant=random_tenant,
            username=username,
            owners=owners,
            app_codes=app_codes,
        )
        url = reverse("virtual_user.retrieve_update_destroy", kwargs={"id": virtual_user.id})
        resp = api_client.delete(url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        with pytest.raises(TenantUser.DoesNotExist):
            TenantUser.objects.get(id=virtual_user.id)

        with pytest.raises(DataSourceUser.DoesNotExist):
            DataSourceUser.objects.get(username=username)

        assert not VirtualUserAppRelation.objects.filter(tenant_user=virtual_user).exists()

        assert not VirtualUserOwnerRelation.objects.filter(tenant_user=virtual_user).exists()
