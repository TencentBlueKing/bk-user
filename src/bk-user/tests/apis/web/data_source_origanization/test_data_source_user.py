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

import pytest
from bkuser.apps.data_source.models import DataSourceUser
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestDataSourceUserWithCustomField:
    def test_create_data_source_user_with_custom_field(self, api_client, custom_fields, default_tenant, data_source):
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

        response = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": data_source.id}), data=user_data
        )

        assert response.status_code == status.HTTP_201_CREATED

        created_user = DataSourceUser.objects.get(username=user_data["username"], data_source=data_source)
        assert created_user.extras == default_extras

    def test_list_data_source_user_with_custom_field(
        self, api_client, data_source_users, default_tenant, custom_fields, data_source
    ):
        extras_data = {field.name: field.default for field in custom_fields}

        update_user_list = []
        for user in data_source_users:
            user.extras = extras_data
            update_user_list.append(user)
        DataSourceUser.objects.bulk_update(update_user_list, fields=["extras"])

        response = api_client.get(reverse("data_source_user.list_create", kwargs={"id": data_source.id}))
        assert response.status_code == status.HTTP_200_OK
        for item in response.data["results"]:
            assert item["extras"] == extras_data

    def test_retrieve_data_source_user_with_custom_field(self, custom_fields, api_client, data_source_users):
        extras = {field.name: field.default for field in custom_fields}
        data_source_user = random.choice(list(data_source_users))
        data_source_user.extras = extras
        data_source_user.save()

        response = api_client.get(reverse("data_source_user.retrieve_update", kwargs={"id": data_source_user.id}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["extras"] == extras

    def test_update_data_source_user_with_custom_field(self, custom_fields, api_client, data_source_users):
        extras = {field.name: field.default for field in custom_fields}
        random_data_source_user = random.choice(list(data_source_users))

        update_user_data = {
            "full_name": f"test-{random_data_source_user.full_name}",
            "department_ids": [],
            "leader_ids": [],
            "email": f"test-{random_data_source_user.full_name}@qq.com",
            "phone_country_code": "+86",
            "phone": "13123456789",
            "extras": extras,
        }

        response = api_client.put(
            reverse("data_source_user.retrieve_update", kwargs={"id": random_data_source_user.id}),
            data=update_user_data,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        data_source_user = DataSourceUser.objects.get(id=random_data_source_user.id)
        for key, value in update_user_data.items():
            if key in ["department_ids", "leader_ids"]:
                continue
            assert getattr(data_source_user, key) == value

    @pytest.mark.parametrize(
        "invalid_extras",
        [
            # 缺少必填字段
            {
                "test_not_required": 1,
            },
            # 未提供选填字段
            {
                "test_num": 1,
                "test_str": "test",
                "test_enum": "test_a",
                "test_multi_enum": ["test_a"],
            },
            # 单选枚举字段非法选项
            {
                "test_num": 1,
                "test_str": "test",
                "test_enum": "test_c",
                "test_multi_enum": ["test_a"],
                "test_not_required": 1,
            },
            # 多选枚举字段非法选项
            {
                "test_num": 1,
                "test_str": "test",
                "test_enum": "test_a",
                "test_multi_enum": ["test_d", "test_e"],
                "test_not_required": 1,
            },
            # 多选枚举字段非法格式
            {
                "test_num": 1,
                "test_str": "test",
                "test_enum": "test_a",
                "test_multi_enum": "test_a",
                "test_not_required": 1,
            },
            # 非法字段
            {
                "test_num": 1,
                "test_str": "test",
                "test_enum": "test_a",
                "test_multi_enum": ["test_a"],
                "test_not_required": 1,
                "test_invalid": "test",
            },
        ],
    )
    def test_create_data_source_user_with_invalid_custom_field_data(
        self, api_client, default_tenant, custom_fields, invalid_extras, data_source
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
        response = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": data_source.id}), data=user_data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        "invalid_extras",
        [
            # 缺少必填字段
            {
                "test_not_required": 1,
            },
            # 未提供选填字段
            {
                "test_num": 1,
                "test_str": "test",
                "test_enum": "test_a",
                "test_multi_enum": ["test_a"],
            },
            # 单选枚举字段非法选项
            {
                "test_num": 1,
                "test_str": "test",
                "test_enum": "test_c",
                "test_multi_enum": ["test_a"],
                "test_not_required": 1,
            },
            # 多选枚举字段非法选项
            {
                "test_num": 1,
                "test_str": "test",
                "test_enum": "test_a",
                "test_multi_enum": ["test_d", "test_e"],
                "test_not_required": 1,
            },
            # 多选枚举字段非法格式
            {
                "test_num": 1,
                "test_str": "test",
                "test_enum": "test_a",
                "test_multi_enum": "test_a",
                "test_not_required": 1,
            },
            # 非法字段
            {
                "test_num": 1,
                "test_str": "test",
                "test_enum": "test_a",
                "test_multi_enum": ["test_a"],
                "test_not_required": 1,
                "test_invalid": "test",
            },
        ],
    )
    def test_update_data_source_user_with_invalid_custom_field_data(
        self, custom_fields, api_client, data_source_users, invalid_extras
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
