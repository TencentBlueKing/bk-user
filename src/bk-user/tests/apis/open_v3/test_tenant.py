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
from unittest import mock

import pytest
from bkuser.apis.open_v3.mixins import OpenApiCommonMixin
from bkuser.apps.tenant.constants import UserFieldDataType
from django.test.utils import override_settings
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestTenantListApi:
    def test_global_tenant_app(self, api_client, mock_request_app, default_tenant, random_tenant):
        with mock_request_app(tenant_mode="global"):
            resp = api_client.get(reverse("open_v3.tenant.list"))

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["id"] for t in resp.data} == {default_tenant.id, random_tenant.id}
        assert set(resp.data[0].keys()) == {"id", "name", "status"}

    @pytest.mark.parametrize(
        ("verified", "tenant_mode"),
        [
            # 单租户应用
            (True, "single"),
            # JWT 中未携带租户模式
            (True, ""),
            # 未认证的全租户应用
            (False, "global"),
        ],
    )
    def test_forbidden_app(self, api_client, mock_request_app, random_tenant, verified, tenant_mode):
        with mock_request_app(verified=verified, tenant_mode=tenant_mode, tenant_id=random_tenant.id):
            resp = api_client.get(reverse("open_v3.tenant.list"))

        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_without_app(self, api_client):
        with mock.patch.object(OpenApiCommonMixin, "authentication_classes", []):
            resp = api_client.get(reverse("open_v3.tenant.list"))

        assert resp.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize("tenant_mode", ["single", ""])
    def test_single_tenant_deploy_with_any_app(self, api_client, mock_request_app, default_tenant, tenant_mode):
        with override_settings(ENABLE_MULTI_TENANT_MODE=False), mock_request_app(tenant_mode=tenant_mode):
            resp = api_client.get(reverse("open_v3.tenant.list"))

        assert resp.status_code == status.HTTP_200_OK
        assert default_tenant.id in {t["id"] for t in resp.data}

    def test_single_tenant_deploy_with_unverified_app(self, api_client, mock_request_app):
        with override_settings(ENABLE_MULTI_TENANT_MODE=False), mock_request_app(verified=False):
            resp = api_client.get(reverse("open_v3.tenant.list"))

        assert resp.status_code == status.HTTP_403_FORBIDDEN


class TestTenantCommonVariableListApi:
    def test_standard(self, api_client, tenant_common_variable):
        resp = api_client.get(reverse("open_v3.tenant_common_variable.list"))
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["name"] for t in resp.data} == {"key_1", "key_2"}
        assert {t["value"] for t in resp.data} == {"value_1", "value_2"}


class TestTenantUserCustomEnumFieldListApi:
    def test_standard(self, api_client, tenant_user_custom_fields):
        resp = api_client.get(reverse("open_v3.tenant_user_custom_enum_field.list"))
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["name"] for t in resp.data} == {"gender", "sport_hobby"}
        assert {t["display_name"] for t in resp.data} == {"性别", "运动爱好"}
        assert {t["data_type"] for t in resp.data} == {UserFieldDataType.ENUM, UserFieldDataType.MULTI_ENUM}
        assert [{"id": "male", "value": "男"}, {"id": "female", "value": "女"}, {"id": "other", "value": "其他"}] in [
            t["options"] for t in resp.data
        ]
        assert [
            {"id": "running", "value": "跑步"},
            {"id": "swimming", "value": "游泳"},
            {"id": "basketball", "value": "篮球"},
            {"id": "football", "value": "足球"},
            {"id": "golf", "value": "高尔夫"},
            {"id": "cycling", "value": "骑行"},
        ] in [t["options"] for t in resp.data]
