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
import random
from typing import Any, Dict

import pytest
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.plugins.constants import DataSourcePluginEnum
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def check_extras(extras: Dict[str, Any], original_extras: Dict[str, Any]):
    for key, value in extras.items():
        assert key in original_extras
        assert value == original_extras[key]


class TestCustomField:
    def test_create_normal_custom_field(self, bk_user, api_client, default_tenant):
        input_field = {
            "tenant": default_tenant.id,
            "name": "test_num",
            "display_name": "数字测试",
            "data_type": UserFieldDataType.NUMBER,
            "required": False,
            "default": 0,
            "options": [],
        }
        resp = api_client.post(reverse("tenant_setting_custom_fields.create"), data=input_field)
        assert resp.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize(
        ("name", "display_name", "required", "data_type", "options", "default"),
        [
            ("111invalid_name", "111invalid_name", False, UserFieldDataType.STRING, [], ""),
            ("duplicate_builtin_field_display_name", "用户名", False, UserFieldDataType.STRING, [], ""),
            ("username", "展示名称重复", False, UserFieldDataType.STRING, [], ""),
            ("enum_options_empty", "invalid_enum_options", False, UserFieldDataType.ENUM, [], ""),
            (
                "enum_options_empty",
                "invalid_enum_options",
                False,
                UserFieldDataType.ENUM,
                [{"id": "", "value": ""}],
                "",
            ),
            (
                "enum_options_id_duplicate",
                "invalid_enum_options",
                False,
                UserFieldDataType.ENUM,
                [{"id": "a", "value": "1"}, {"id": "a", "value": "2"}],
                "",
            ),
            (
                "enum_options_value_duplicate",
                "invalid_enum_options",
                False,
                UserFieldDataType.ENUM,
                [{"id": "a", "value": "1"}, {"id": "b", "value": "1"}],
                "",
            ),
            (
                "invalid_enum_options",
                "invalid_enum_options",
                False,
                UserFieldDataType.ENUM,
                [{"id": "", "value": ""}],
                "",
            ),
            (
                "invalid_enum_default",
                "invalid_enum_default",
                False,
                UserFieldDataType.ENUM,
                [{"id": "a", "value": "1"}],
                "b",
            ),
            (
                "invalid_enum_default",
                "invalid_enum_default",
                False,
                UserFieldDataType.ENUM,
                [{"id": "a", "value": "1"}],
                ["a"],
            ),
            (
                "invalid_multi_enum_default",
                "invalid_enum_default",
                False,
                UserFieldDataType.MULTI_ENUM,
                [{"id": "a", "value": "1"}],
                "a",
            ),
            (
                "invalid_multi_enum_default",
                "invalid_enum_default",
                False,
                UserFieldDataType.MULTI_ENUM,
                [{"id": "a", "value": "1"}],
                ["b"],
            ),
        ],
    )
    def test_create_custom_field_with_invalid_data(
        self, bk_user, api_client, default_tenant, name, display_name, required, data_type, options, default
    ):
        input_field = {
            "tenant": default_tenant.id,
            "name": name,
            "display_name": display_name,
            "data_type": data_type,
            "required": required,
            "default": default,
            "options": options,
        }
        resp = api_client.post(reverse("tenant_setting_custom_fields.create"), data=input_field)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


class TestDataSourceUserWithCustomField:
    def test_create_data_source_user_with_custom_field(self, bk_user, api_client, custom_fields, default_tenant):
        default_extras = {field.name: field.default for field in custom_fields}
        user_data = {
            "username": "test",
            "full_name": "test",
            "department_ids": [],
            "leader_ids": [],
            "email": "testerA@qq.com",
            "phone_country_code": "+86",
            "phone": "13123456789",
            "extras": default_extras,
        }
        data_source = DataSource.objects.get(
            owner_tenant_id=default_tenant.id,
            name=f"{default_tenant.id}-default-local",
            plugin_id=DataSourcePluginEnum.LOCAL,
        )
        response = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": data_source.id}), data=user_data
        )

        assert response.status_code == status.HTTP_201_CREATED

        created_user = DataSourceUser.objects.get(username=user_data["username"], data_source=data_source)
        check_extras(created_user.extras, default_extras)

    def test_list_data_source_user_with_custom_field(
        self, bk_user, api_client, data_source_users, default_tenant, custom_fields
    ):
        extras_data = {field.name: field.default for field in custom_fields}
        data_source = DataSource.objects.get(
            owner_tenant_id=default_tenant.id,
            name=f"{default_tenant.id}-default-local",
            plugin_id=DataSourcePluginEnum.LOCAL,
        )

        for user in data_source_users:
            user.extras = extras_data
            user.save()

        response = api_client.get(reverse("data_source_user.list_create", kwargs={"id": data_source.id}))
        assert response.status_code == status.HTTP_200_OK
        for item in response.data["results"]:
            check_extras(item["extras"], extras_data)

    def test_retrieve_data_source_user_with_custom_field(self, bk_user, custom_fields, api_client, data_source_users):
        extras = {field.name: field.default for field in custom_fields}
        data_source_user = random.choice(list(data_source_users))
        data_source_user.extras = extras
        data_source_user.save()

        response = api_client.get(reverse("data_source_user.retrieve_update", kwargs={"id": data_source_user.id}))
        assert response.status_code == status.HTTP_200_OK
        check_extras(response.data["extras"], extras)

    @pytest.mark.parametrize(
        "invalid_extras",
        [
            {},
            {"test_num": 1, "test_str": "test", "test_enum": "test_c", "test_multi_enum": ["test_a"]},
            {"test_num": 1, "test_str": "test", "test_enum": "test_a", "test_multi_enum": "test_a"},
            {
                "test_num": 1,
                "test_str": "test",
                "test_enum": "test_a",
                "test_multi_enum": ["test_a"],
                "test_invalid": "test",
            },
        ],
    )
    def test_create_data_source_user_with_invalid_custom_field_data(
        self, bk_user, api_client, default_tenant, custom_fields, invalid_extras
    ):
        user_data = {
            "username": "test",
            "full_name": "test",
            "department_ids": [],
            "leader_ids": [],
            "email": "testerA@qq.com",
            "phone_country_code": "+86",
            "phone": "13123456789",
            "extras": invalid_extras,
        }
        print(111111111111111111, user_data)
        data_source = DataSource.objects.get(
            owner_tenant_id=default_tenant.id,
            name=f"{default_tenant.id}-default-local",
            plugin_id=DataSourcePluginEnum.LOCAL,
        )
        response = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": data_source.id}), data=user_data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        "invalid_extras",
        [
            {},
            {"test_num": 1, "test_str": "test", "test_enum": "test_c", "test_multi_enum": ["test_a"]},
            {"test_num": 1, "test_str": "test", "test_enum": "test_a", "test_multi_enum": "test_a"},
            {
                "test_num": 1,
                "test_str": "test",
                "test_enum": "test_a",
                "test_multi_enum": ["test_a"],
                "test_invalid": "test",
            },
        ],
    )
    def test_update_data_source_user_with_invalid_custom_field_data(
        self, bk_user, custom_fields, api_client, data_source_users, invalid_extras
    ):
        data_source_user = random.choice(list(data_source_users))

        update_data = {
            "full_name": "testerA-1",
            "department_ids": [],
            "leader_ids": [],
            "email": "testerA-1@qq.com",
            "phone_country_code": "+86",
            "phone": "13123456799",
            "extras": invalid_extras,
        }
        response = api_client.put(
            reverse("data_source_user.retrieve_update", kwargs={"id": data_source_user.id}), data=update_data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestTenantUserWithCustomField:
    def _add_extras_for_tenant_user(self, extras, tenant_users):
        for tenant_user in tenant_users:
            data_source_user = tenant_user.data_source_user
            data_source_user.extras = extras
            data_source_user.save()

    def test_retrieve_tenant_user_with_custom_field(self, bk_user, custom_fields, api_client, tenant_users):
        extras = {field.name: field.default for field in custom_fields}
        self._add_extras_for_tenant_user(extras, tenant_users)

        user = random.choice(list(tenant_users))
        response = api_client.get(reverse("department.users.retrieve", kwargs={"id": user.id}))
        assert response.status_code == status.HTTP_200_OK
        check_extras(response.data["extras"], extras)

        response = api_client.get(reverse("department.users.retrieve", kwargs={"id": bk_user.username}))
        assert response.status_code == status.HTTP_200_OK
        check_extras(response.data["extras"], extras)

    def test_list_tenant_user_with_custom_field(
        self, bk_user, custom_fields, api_client, tenant_users, default_tenant, tenant_departments
    ):
        extras = {field.name: field.default for field in custom_fields}
        self._add_extras_for_tenant_user(extras, tenant_users)

        # 租户下展示用户
        response = api_client.get(reverse("organization.tenant.users.list", kwargs={"id": default_tenant.id}))
        assert response.status_code == status.HTTP_200_OK
        for user in response.data["results"]:
            check_extras(user["extras"], extras)

        # 部门下用户
        tenant_department = random.choice(list(tenant_departments))
        response = api_client.get(reverse("departments.users.list", kwargs={"id": tenant_department.id}))
        assert response.status_code == status.HTTP_200_OK
        for user in response.data["results"]:
            check_extras(user["extras"], extras)
