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
from bkuser.apps.tenant.constants import UserFieldDataType
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestCustomField:
    def test_create_normal_custom_field(self, api_client):
        input_field = {
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
            ("invalid_num_field", "invalid_num_field", False, UserFieldDataType.NUMBER, [], "invalid_num_field"),
            ("duplicate_builtin_field_display_name", "用户名", False, UserFieldDataType.STRING, [], ""),
            ("username", "用户名重复", False, UserFieldDataType.STRING, [], ""),
            ("enum_options_empty", "invalid_enum_options", False, UserFieldDataType.ENUM, [], ""),
            (
                "enum_field_default_empty",
                "enum_field_default_empty",
                False,
                UserFieldDataType.ENUM,
                [{"id": "a", "value": "1"}, {"id": "b", "value": "2"}],
                "",
            ),
            (
                "enum_multi_field_default_empty",
                "enum_multi_field_default_empty",
                False,
                UserFieldDataType.ENUM,
                [{"id": "a", "value": "1"}, {"id": "b", "value": "2"}],
                [],
            ),
            (
                "enum_options_id_duplicate",
                "enum_options_id_duplicate",
                False,
                UserFieldDataType.ENUM,
                [{"id": "a", "value": "1"}, {"id": "a", "value": "2"}],
                "",
            ),
            (
                "enum_options_value_duplicate",
                "enum_options_value_duplicate",
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
                "invalid_multi_enum_default",
                False,
                UserFieldDataType.MULTI_ENUM,
                [{"id": "a", "value": "1"}],
                "a",
            ),
            (
                "invalid_multi_enum_default",
                "invalid_multi_enum_default",
                False,
                UserFieldDataType.MULTI_ENUM,
                [{"id": "a", "value": "1"}],
                ["b"],
            ),
        ],
    )
    def test_create_custom_field_with_invalid_data(
        self, api_client, name, display_name, required, data_type, options, default
    ):
        input_field = {
            "name": name,
            "display_name": display_name,
            "required": required,
            "data_type": data_type,
            "options": options,
            "default": default,
        }
        resp = api_client.post(reverse("tenant_setting_custom_fields.create"), data=input_field)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
