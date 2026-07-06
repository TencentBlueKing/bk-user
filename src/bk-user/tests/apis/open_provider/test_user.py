# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
from bkuser.apps.tenant.models import TenantUser
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestUserBatchCreate:
    def test_standard(self, api_client, full_local_data_source):
        resp = api_client.post(
            reverse("open_provider.user.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={
                "users": [
                    {
                        "id": "emp_001",
                        "username": "newuser1",
                        "full_name": "新用户1",
                        "email": "newuser1@example.com",
                        "phone": "13800000001",
                    },
                    {
                        "id": "emp_002",
                        "username": "newuser2",
                        "full_name": "新用户2",
                    },
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert DataSourceUser.objects.filter(data_source=full_local_data_source, code="emp_001").exists()
        assert DataSourceUser.objects.filter(data_source=full_local_data_source, code="emp_002").exists()
        assert TenantUser.objects.filter(data_source_user__code="emp_001").exists()

    def test_empty_users(self, api_client, full_local_data_source):
        resp = api_client.post(
            reverse("open_provider.user.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={"users": []},
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_username(self, api_client, full_local_data_source):
        resp = api_client.post(
            reverse("open_provider.user.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={
                "users": [
                    {"id": "emp_v1", "username": "-invalid", "full_name": "Test"},
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_email(self, api_client, full_local_data_source):
        resp = api_client.post(
            reverse("open_provider.user.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={
                "users": [
                    {"id": "emp_v2", "username": "validuser", "full_name": "Test", "email": "not-an-email"},
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_id(self, api_client, full_local_data_source):
        resp = api_client.post(
            reverse("open_provider.user.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={
                "users": [
                    {"id": "dup_id", "username": "user1", "full_name": "Test1"},
                    {"id": "dup_id", "username": "user2", "full_name": "Test2"},
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_username(self, api_client, full_local_data_source):
        resp = api_client.post(
            reverse("open_provider.user.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={
                "users": [
                    {"id": "emp_d1", "username": "sameuser", "full_name": "Test1"},
                    {"id": "emp_d2", "username": "sameuser", "full_name": "Test2"},
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_existing_username(self, api_client, full_local_data_source):
        existing_user = DataSourceUser.objects.filter(data_source=full_local_data_source).first()
        resp = api_client.post(
            reverse("open_provider.user.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={
                "users": [
                    {"id": "emp_new", "username": existing_user.username, "full_name": "Test"},
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestUserBatchUpdate:
    def test_standard(self, api_client, full_local_data_source):
        ds_user = DataSourceUser.objects.filter(data_source=full_local_data_source).first()

        resp = api_client.put(
            reverse("open_provider.user.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={
                "users": [
                    {
                        "id": ds_user.code,
                        "full_name": "更新姓名",
                        "email": "updated@example.com",
                    }
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        ds_user.refresh_from_db()
        assert ds_user.full_name == "更新姓名"
        assert ds_user.email == "updated@example.com"

    def test_invalid_username_update(self, api_client, full_local_data_source):
        ds_user = DataSourceUser.objects.filter(data_source=full_local_data_source).first()
        resp = api_client.put(
            reverse("open_provider.user.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={
                "users": [
                    {"id": ds_user.code, "username": "!bad!"},
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_email_update(self, api_client, full_local_data_source):
        ds_user = DataSourceUser.objects.filter(data_source=full_local_data_source).first()
        resp = api_client.put(
            reverse("open_provider.user.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={
                "users": [
                    {"id": ds_user.code, "email": "not-email"},
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestUserBatchDelete:
    def test_standard(self, api_client, full_local_data_source):
        ds_user = DataSourceUser.objects.filter(data_source=full_local_data_source).first()
        code = ds_user.code

        resp = api_client.delete(
            reverse("open_provider.user.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={"ids": [code]},
            format="json",
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not DataSourceUser.objects.filter(data_source=full_local_data_source, code=code).exists()
        assert not TenantUser.objects.filter(data_source_user__code=code).exists()

    def test_nonexistent_user(self, api_client, full_local_data_source):
        resp = api_client.delete(
            reverse("open_provider.user.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={"ids": ["nonexistent_code"]},
            format="json",
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
