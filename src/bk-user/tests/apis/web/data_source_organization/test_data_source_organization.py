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
from bkuser.apps.data_source.models import DataSourceDepartment, DataSourceUser
from django.urls import reverse
from rest_framework import status

from tests.test_utils.data_source_organization import (
    create_data_source_department,
    create_data_source_user,
    generate_data_source_username,
)
from tests.test_utils.helpers import generate_random_string

pytestmark = pytest.mark.django_db


@pytest.fixture()
def data_source_user(local_data_source) -> DataSourceUser:
    return create_data_source_user(data_source_id=local_data_source.id)


@pytest.fixture()
def data_source_department(local_data_source) -> DataSourceDepartment:
    return create_data_source_department(data_source_id=local_data_source.id)


class TestDataSourceUserCreateApi:
    def test_create_local_data_source_user(self, api_client, local_data_source):
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data={
                "username": generate_data_source_username(),
                "full_name": generate_random_string(),
                "email": "test@example.com",
                "phone": "13000000000",
            },
        )
        assert resp.status_code == status.HTTP_200_OK

    def test_create_without_username(self, api_client, local_data_source):
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data={"full_name": generate_data_source_username(), "email": "test@example.com", "phone": "13000000000"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: username: 该字段是必填项。" in resp.data["message"]

    def test_create_without_fullname(self, api_client, local_data_source):
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data={"username": generate_data_source_username(), "email": "test@example.com", "phone": "13000000000"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: full_name: 该字段是必填项。" in resp.data["message"]

    def test_create_without_email(self, api_client, local_data_source):
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data={
                "full_name": generate_random_string(),
                "username": generate_data_source_username(),
                "phone": "13000000000",
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: email: 该字段是必填项。" in resp.data["message"]

    def test_create_without_phone(self, api_client, local_data_source):
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data={
                "username": generate_data_source_username(),
                "full_name": generate_random_string(),
                "email": "test@example.com",
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: phone: 该字段是必填项。" in resp.data["message"]

    def test_create_with_invalid_username(self, api_client, local_data_source):
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data={
                "username": ".error_username",
                "full_name": generate_random_string(),
                "email": "test@example.com",
                "phone": "13000000000",
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不符合 用户名 的命名规范" in resp.data["message"]

    def test_create_with_invalid_email(self, api_client, local_data_source):
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data={
                "username": generate_data_source_username(),
                "full_name": generate_random_string(),
                "email": "test.com",
                "phone": "13000000000",
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "参数校验不通过: email: 请输入合法的邮件地址。" in resp.data["message"]

    def test_create_with_incorrect_length_phone(self, api_client, local_data_source):
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data={
                "username": generate_data_source_username(),
                "full_name": generate_random_string(),
                "email": "test@example.com",
                "phone": "130",
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "手机号码解析异常: 手机号 130 长度异常" in resp.data["message"]

    def test_create_with_invalid_phone(self, api_client, local_data_source):
        resp = api_client.post(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data={
                "username": generate_data_source_username(),
                "full_name": generate_random_string(),
                "email": "test@example.com",
                "phone": "aaaaaaaaaaa",
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "手机号码解析异常: 手机号 aaaaaaaaaaa 解析异常" in resp.data["message"]


class TestDataSourceUserListApi:
    def test_list(self, api_client, local_data_source):
        resp = api_client.get(reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}))

        assert DataSourceUser.objects.filter(data_source_id=local_data_source.id).count() == resp.data["count"]

        for item in resp.data["results"]:
            data_source_user = DataSourceUser.objects.filter(id=item["id"]).first()
            assert data_source_user is not None
            assert data_source_user.username == item["username"]
            assert data_source_user.full_name == item["full_name"]
            assert data_source_user.phone == item["phone"]
            assert data_source_user.email == item["email"]
            assert data_source_user.departments == item["departments"]

    def test_list_with_username(self, api_client, local_data_source, data_source_user):
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

        assert DataSourceUser.objects.filter(data_source_id=local_data_source.id).count() == resp.data["count"]

        for item in resp.data["results"]:
            data_source_user = DataSourceUser.objects.filter(id=item["id"]).first()
            assert data_source_user is not None
            assert data_source_user.id == item["id"]
            assert data_source_user.username == item["username"]

    def test_list_with_keyword(self, api_client, local_data_source, data_source_user):
        resp = api_client.get(
            reverse("data_source_user.list_create", kwargs={"id": local_data_source.id}),
            data={"keyword": data_source_user.username},
        )

        assert resp.data["count"] == 1
        user = resp.data["results"][0]

        assert user["username"] == data_source_user.username


class TestDataSourceDepartmentsListApi:
    def test_list(self, api_client, local_data_source):
        resp = api_client.get(reverse("data_source_department.list", kwargs={"id": local_data_source.id}))

        assert DataSourceDepartment.objects.filter(data_source_id=local_data_source.id).count() == resp.data["count"]

        for item in resp.data["results"]:
            data_source_department = DataSourceDepartment.objects.filter(id=item["id"]).first()
            assert data_source_department is not None
            assert data_source_department.id == item["id"]
            assert data_source_department.name == item["name"]

    def test_list_with_keyword(self, api_client, local_data_source, data_source_department):
        resp = api_client.get(
            reverse("data_source_department.list", kwargs={"id": local_data_source.id}),
            data={"keyword": data_source_department.name},
        )

        assert resp.data["count"] == 1
        department = resp.data["results"][0]

        assert department["name"] == data_source_department.name
