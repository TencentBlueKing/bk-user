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
from typing import Any, Dict, List

import pytest
from bkuser.apps.data_source.models import DataSourceDepartment, DataSourceUser
from django.urls import reverse
from rest_framework import status

from tests.test_utils.data_source_organization import (
    create_data_source_departments,
    create_data_source_users,
    generate_data_source_username,
)
from tests.test_utils.helpers import generate_random_string

pytestmark = pytest.mark.django_db


@pytest.fixture()
def data_source_user_base_info() -> Dict[str, Any]:
    return {
        "username": generate_data_source_username(),
        "full_name": generate_random_string(),
        "email": "test@example.com",
        "phone": "13000000000",
    }


@pytest.fixture()
def data_source_departments(local_data_source) -> List[DataSourceDepartment]:
    return create_data_source_departments(data_source=local_data_source)


@pytest.fixture()
def data_source_users(local_data_source, data_source_departments) -> List[DataSourceUser]:
    return create_data_source_users(data_source=local_data_source, departments=data_source_departments)


class TestDataSourceUserCreateApi:
    def test_create_local_data_source_user(self, api_client, local_data_source, data_source_user_base_info):
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data=data_source_user_base_info,
        )
        assert resp.status_code == status.HTTP_200_OK

    def test_create_without_username(self, api_client, local_data_source, data_source_user_base_info):
        data_source_user_base_info.pop("username")
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data=data_source_user_base_info,
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: username: 该字段是必填项。" in resp.data["message"]

    def test_create_without_fullname(self, api_client, local_data_source, data_source_user_base_info):
        data_source_user_base_info.pop("full_name")
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data=data_source_user_base_info,
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: full_name: 该字段是必填项。" in resp.data["message"]

    def test_create_without_email(self, api_client, local_data_source, data_source_user_base_info):
        data_source_user_base_info.pop("email")
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data=data_source_user_base_info,
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: email: 该字段是必填项。" in resp.data["message"]

    def test_create_without_phone(self, api_client, local_data_source, data_source_user_base_info):
        data_source_user_base_info.pop("phone")
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data=data_source_user_base_info,
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: phone: 该字段是必填项。" in resp.data["message"]

    def test_create_with_invalid_username(self, api_client, local_data_source, data_source_user_base_info):
        data_source_user_base_info["username"] = ".error_username"
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data=data_source_user_base_info,
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不符合 用户名 的命名规范" in resp.data["message"]

    def test_create_with_invalid_email(self, api_client, local_data_source, data_source_user_base_info):
        data_source_user_base_info["email"] = "test.com"
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data=data_source_user_base_info,
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: email: 请输入合法的邮件地址。" in resp.data["message"]

    def test_create_with_incorrect_length_phone(self, api_client, local_data_source, data_source_user_base_info):
        data_source_user_base_info["phone"] = "130"
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data=data_source_user_base_info,
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "手机号码解析异常: 手机号 130 长度异常" in resp.data["message"]

    def test_create_with_invalid_phone(self, api_client, local_data_source, data_source_user_base_info):
        data_source_user_base_info["phone"] = "aaaaaaaaaaa"
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data=data_source_user_base_info,
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "手机号码解析异常: 手机号 aaaaaaaaaaa 解析异常" in resp.data["message"]


class TestDataSourceUserListApi:
    def test_list(self, api_client, local_data_source):
        resp = api_client.get(reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}))

        assert DataSourceUser.objects.filter(data_source=local_data_source).count() == resp.data["count"]

        for item in resp.data["results"]:
            data_source_user = DataSourceUser.objects.filter(id=item["id"]).first()
            assert data_source_user is not None
            assert data_source_user.username == item["username"]
            assert data_source_user.full_name == item["full_name"]
            assert data_source_user.phone == item["phone"]
            assert data_source_user.email == item["email"]
            assert data_source_user.departments == item["departments"]

    def test_list_with_username(self, api_client, local_data_source, data_source_users):
        data_source_user = random.choice(data_source_users)
        resp = api_client.get(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data={"username": data_source_user.username},
        )

        assert resp.data["count"] == 1
        user = resp.data["results"][0]
        assert user["username"] == data_source_user.username
        assert user["full_name"] == data_source_user.full_name
        assert user["phone"] == data_source_user.phone
        assert user["email"] == data_source_user.email


class TestDataSourceLeadersListApi:
    def test_list(self, api_client, local_data_source):
        resp = api_client.get(reverse("data_source_leader.list", kwargs={"id": local_data_source.id}))

        assert DataSourceUser.objects.filter(data_source=local_data_source).count() == resp.data["count"]

        for item in resp.data["results"]:
            data_source_user = DataSourceUser.objects.filter(id=item["id"]).first()
            assert data_source_user is not None
            assert data_source_user.id == item["id"]
            assert data_source_user.username == item["username"]

    def test_list_with_keyword(self, api_client, local_data_source, data_source_users):
        data_source_user = random.choice(data_source_users)
        resp = api_client.get(
            reverse("data_source_leader.list", kwargs={"id": local_data_source.id}),
            data={"keyword": data_source_user.username},
        )

        user = resp.data["results"][0]
        assert user["username"] in [data_source_user.username, data_source_user.full_name]


class TestDataSourceDepartmentsListApi:
    def test_list(self, api_client, local_data_source):
        resp = api_client.get(reverse("data_source_department.list", kwargs={"id": local_data_source.id}))

        assert DataSourceDepartment.objects.filter(data_source=local_data_source).count() == resp.data["count"]

        for item in resp.data["results"]:
            data_source_department = DataSourceDepartment.objects.filter(id=item["id"]).first()
            assert data_source_department is not None
            assert data_source_department.id == item["id"]
            assert data_source_department.name == item["name"]

    def test_list_with_keyword(self, api_client, local_data_source, data_source_departments):
        data_source_department = random.choice(data_source_departments)
        resp = api_client.get(
            reverse("data_source_department.list", kwargs={"id": local_data_source.id}),
            data={"name": data_source_department.name},
        )

        assert resp.data["count"] == 1
        department = resp.data["results"][0]
        assert department["name"] == data_source_department.name


class TestDataSourceUserUpdateApi:
    def test_update_local_data_source_user(self, api_client, data_source_users):
        data_source_user = random.choice(data_source_users)
        resp = api_client.put(
            reverse("data_source_user.retrieve_update", kwargs={"id": data_source_user.id}),
            data={
                "full_name": data_source_user.full_name,
                "email": "test@update.com",
                "phone_country_code": data_source_user.phone_country_code,
                "phone": data_source_user.phone,
                "leader_ids": [],
                "department_ids": [],
            },
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        resp = api_client.get(reverse("data_source_user.retrieve_update", kwargs={"id": data_source_user.id}))
        assert resp.data["email"] == "test@update.com"

    def test_update_local_data_source_user_without_full_name(self, api_client, data_source_users):
        data_source_user = random.choice(data_source_users)
        resp = api_client.put(
            reverse("data_source_user.retrieve_update", kwargs={"id": data_source_user.id}),
            data={
                "email": data_source_user.email,
                "phone_country_code": data_source_user.phone_country_code,
                "phone": data_source_user.phone,
                "leader_ids": [],
                "department_ids": [],
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: full_name: 该字段是必填项。" in resp.data["message"]

    def test_update_local_data_source_user_without_email(self, api_client, data_source_users):
        data_source_user = random.choice(data_source_users)
        resp = api_client.put(
            reverse("data_source_user.retrieve_update", kwargs={"id": data_source_user.id}),
            data={
                "full_name": data_source_user.full_name,
                "phone_country_code": data_source_user.phone_country_code,
                "phone": data_source_user.phone,
                "leader_ids": [],
                "department_ids": [],
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: email: 该字段是必填项。" in resp.data["message"]

    def test_update_local_data_source_user_without_phone_country_code(self, api_client, data_source_users):
        data_source_user = random.choice(data_source_users)
        resp = api_client.put(
            reverse("data_source_user.retrieve_update", kwargs={"id": data_source_user.id}),
            data={
                "full_name": data_source_user.full_name,
                "email": data_source_user.email,
                "phone": data_source_user.phone,
                "leader_ids": [],
                "department_ids": [],
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: phone_country_code: 该字段是必填项。" in resp.data["message"]

    def test_update_local_data_source_user_without_phone(self, api_client, data_source_users):
        data_source_user = random.choice(data_source_users)
        resp = api_client.put(
            reverse("data_source_user.retrieve_update", kwargs={"id": data_source_user.id}),
            data={
                "full_name": data_source_user.full_name,
                "email": data_source_user.email,
                "phone_country_code": data_source_user.phone_country_code,
                "leader_ids": [],
                "department_ids": [],
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: phone: 该字段是必填项。" in resp.data["message"]

    def test_update_local_data_source_user_without_leader_ids(self, api_client, data_source_users):
        data_source_user = random.choice(data_source_users)
        resp = api_client.put(
            reverse("data_source_user.retrieve_update", kwargs={"id": data_source_user.id}),
            data={
                "full_name": data_source_user.full_name,
                "email": data_source_user.email,
                "phone_country_code": data_source_user.phone_country_code,
                "phone": data_source_user.phone,
                "department_ids": [],
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: leader_ids: 该字段是必填项。" in resp.data["message"]

    def test_update_local_data_source_user_without_department_ids(self, api_client, data_source_users):
        data_source_user = random.choice(data_source_users)
        resp = api_client.put(
            reverse("data_source_user.retrieve_update", kwargs={"id": data_source_user.id}),
            data={
                "full_name": data_source_user.full_name,
                "email": data_source_user.email,
                "phone_country_code": data_source_user.phone_country_code,
                "phone": data_source_user.phone,
                "leader_ids": [],
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: department_ids: 该字段是必填项。" in resp.data["message"]

    def test_update_local_data_source_user_with_invalid_email(self, api_client, data_source_users):
        data_source_user = random.choice(data_source_users)

        resp = api_client.put(
            reverse("data_source_user.retrieve_update", kwargs={"id": data_source_user.id}),
            data={
                "full_name": data_source_user.full_name,
                "email": "test.com",
                "phone_country_code": data_source_user.phone_country_code,
                "phone": data_source_user.phone,
                "leader_ids": [],
                "department_ids": [],
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: email: 请输入合法的邮件地址。" in resp.data["message"]

    def test_update_local_data_source_user_with_invalid_phone(self, api_client, data_source_users):
        data_source_user = random.choice(data_source_users)

        resp = api_client.put(
            reverse("data_source_user.retrieve_update", kwargs={"id": data_source_user.id}),
            data={
                "full_name": data_source_user.full_name,
                "email": data_source_user.email,
                "phone_country_code": data_source_user.phone_country_code,
                "phone": "aaaaaaaaaaa",
                "leader_ids": [],
                "department_ids": [],
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "手机号码解析异常: 手机号 aaaaaaaaaaa 解析异常" in resp.data["message"]

    def test_update_local_data_source_user_with_incorrect_length_phone(self, api_client, data_source_users):
        data_source_user = random.choice(data_source_users)

        resp = api_client.put(
            reverse("data_source_user.retrieve_update", kwargs={"id": data_source_user.id}),
            data={
                "full_name": data_source_user.full_name,
                "email": data_source_user.email,
                "phone_country_code": data_source_user.phone_country_code,
                "phone": "130",
                "leader_ids": [],
                "department_ids": [],
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "手机号码解析异常: 手机号 130 长度异常" in resp.data["message"]


class TestDataSourceUserRetrieveApi:
    def test_retrieve(self, api_client, data_source_users):
        data_source_user = random.choice(data_source_users)
        resp = api_client.get(reverse("data_source_user.retrieve_update", kwargs={"id": data_source_user.id}))

        assert resp.data["username"] == data_source_user.username
        assert resp.data["full_name"] == data_source_user.full_name
        assert resp.data["email"] == data_source_user.email
        assert resp.data["phone_country_code"] == data_source_user.phone_country_code
        assert resp.data["phone"] == data_source_user.phone
        assert resp.data["logo"] == data_source_user.logo
