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
from django.test.utils import override_settings
from django.urls import reverse
from rest_framework import status

from tests.test_utils.auth import make_gateway_user
from tests.test_utils.helpers import generate_random_string

pytestmark = pytest.mark.django_db

OPEN_WEB_APIS = [
    ("get", "open_web.data_source_owner_tenant.list", {}),
    ("put", "open_web.tenant.current_user.language.update", {}),
    ("get", "open_web.tenant_user.display_info.list", {}),
    ("get", "open_web.tenant_user.display_info.retrieve", {"id": "zhangsan"}),
    ("get", "open_web.tenant_user.lookup", {}),
    ("get", "open_web.tenant_user.search", {}),
    ("get", "open_web.tenant_department.search", {}),
    ("get", "open_web.tenant_department.lookup", {}),
    ("get", "open_web.tenant_department.child.list", {"id": 0}),
    ("get", "open_web.tenant_department.user.list", {"id": 0}),
    ("get", "open_web.tenant.virtual_user.list", {}),
    ("get", "open_web.tenant.virtual_user.search", {}),
]


class TestIsCurrentUserTenant:
    @pytest.mark.parametrize(("method", "url_name", "kwargs"), OPEN_WEB_APIS)
    def test_header_not_match_user_tenant(self, api_client, method, url_name, kwargs):
        api_client.force_authenticate(user=make_gateway_user(generate_random_string()))

        resp = getattr(api_client, method)(reverse(url_name, kwargs=kwargs))

        assert resp.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(("method", "url_name", "kwargs"), OPEN_WEB_APIS)
    def test_user_without_tenant_in_multi_tenant_mode(self, api_client, method, url_name, kwargs):
        api_client.force_authenticate(user=make_gateway_user(""))

        resp = getattr(api_client, method)(reverse(url_name, kwargs=kwargs))

        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_header_match_user_tenant(self, api_client):
        resp = api_client.get(reverse("open_web.data_source_owner_tenant.list"))

        assert resp.status_code == status.HTTP_200_OK

    def test_without_tenant_header(self, api_client):
        resp = api_client.get(reverse("open_web.data_source_owner_tenant.list"), HTTP_X_BK_TENANT_ID="")

        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_user_without_tenant_in_single_tenant_mode(self, api_client):
        api_client.force_authenticate(user=make_gateway_user(""))

        with override_settings(ENABLE_MULTI_TENANT_MODE=False):
            resp = api_client.get(reverse("open_web.data_source_owner_tenant.list"))

        assert resp.status_code == status.HTTP_200_OK

    def test_user_not_default_tenant_in_single_tenant_mode(self, api_client):
        with override_settings(ENABLE_MULTI_TENANT_MODE=False):
            resp = api_client.get(reverse("open_web.data_source_owner_tenant.list"))

        assert resp.status_code == status.HTTP_403_FORBIDDEN
