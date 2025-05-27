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
from bkuser.apps.tenant.models import TenantUser, TenantUserDisplayNameExpressionConfig
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_create_custom_fields")
class TestTenantUserDisplayNameConfigRetrieveUpdateApi:
    def test_retrieve_display_name_config(self, api_client):
        resp = api_client.get(reverse("tenant_user_display_name_expression_config.retrieve_update"))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["expression"] == "{username}({full_name})"

    def test_update_display_name_config(self, api_client, random_tenant):
        config = TenantUserDisplayNameExpressionConfig.objects.get(tenant=random_tenant)
        assert config.expression == "{username}({full_name})"
        assert set(config.fields["builtin"]) == {"username", "full_name"}
        assert set(config.fields["custom"]) == set()

        resp = api_client.put(
            reverse("tenant_user_display_name_expression_config.retrieve_update"),
            data={"expression": "{username}-{full_name}-{test_num}"},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        config.refresh_from_db()
        assert config.expression == "{username}-{full_name}-{test_num}"
        assert set(config.fields["builtin"]) == {"username", "full_name"}
        assert set(config.fields["custom"]) == {"test_num"}
        assert config.version == 2

    def test_update_display_name_config_without_field(self, api_client):
        resp = api_client.put(
            reverse("tenant_user_display_name_expression_config.retrieve_update"),
            data={"expression": "123"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_display_name_config_with_too_many_fields(self, api_client):
        resp = api_client.put(
            reverse("tenant_user_display_name_expression_config.retrieve_update"),
            data={"expression": "{username}-{full_name}-{email}-{test_str}"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_display_name_config_with_too_many_non_field(self, api_client):
        resp = api_client.put(
            reverse("tenant_user_display_name_expression_config.retrieve_update"),
            data={"expression": "{username}12345678123456781"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_display_name_config_with_invalid_field(self, api_client):
        resp = api_client.put(
            reverse("tenant_user_display_name_expression_config.retrieve_update"),
            data={"expression": "{username}-{full_name}-{test_str2}"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_display_name_config_with_duplicate_field(self, api_client):
        resp = api_client.put(
            reverse("tenant_user_display_name_expression_config.retrieve_update"),
            data={"expression": "{username}-{full_name}-{username}"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_display_name_config_with_not_unique_field(self, api_client):
        resp = api_client.put(
            reverse("tenant_user_display_name_expression_config.retrieve_update"),
            data={"expression": "{phone}-{test_enum}-{test_num}"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("_create_custom_fields")
class TestTenantUserDisplayNameConfigPreviewApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_builtin_fields(self, api_client, random_tenant):
        # 由于租户用户顺序不固定，所以需要提前获取
        tenant_users = TenantUser.objects.filter(tenant=random_tenant)[:3].select_related("data_source_user")
        resp = api_client.post(
            reverse("tenant_user_display_name_expression_config.preview"),
            data={"expression": "{username}({full_name})"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 3
        assert {t["display_name"] for t in resp.data} == {
            f"{t.data_source_user.username}({t.data_source_user.full_name})" for t in tenant_users
        }

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_with_custom_fields(self, api_client, random_tenant):
        tenant_users = TenantUser.objects.filter(tenant=random_tenant)[:3].select_related("data_source_user")
        resp = api_client.post(
            reverse("tenant_user_display_name_expression_config.preview"),
            data={"expression": "{username}({test_num})({test_str})"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 3
        assert {t["display_name"] for t in resp.data} == {
            f"{t.data_source_user.username}({t.data_source_user.phone})({t.data_source_user.username})"
            for t in tenant_users[:3]
        }

    def test_with_not_tenant_user(self, api_client):
        resp = api_client.post(
            reverse("tenant_user_display_name_expression_config.preview"),
            data={"expression": "{username}({full_name})"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["display_name"] == "zhangsan(张三)"
