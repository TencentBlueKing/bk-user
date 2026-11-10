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
from typing import Callable, ContextManager, List
from unittest import mock

import pytest
from apigw_manager.drf.authentication import App
from bkuser.apis.open_v3.mixins import OpenApiCommonMixin
from bkuser.apps.tenant.models import TenantCommonVariable
from django.contrib.auth.models import AnonymousUser
from django.core.cache import caches
from django.test.utils import override_settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.test import APIClient

from tests.test_utils.tenant import sync_users_depts_to_tenant


@pytest.fixture(autouse=True)
def _clear_cache():
    """在每个测试前清除缓存，避免缓存的方法返回值影响测试结果"""
    for cache_name in caches:
        caches[cache_name].clear()
    yield
    for cache_name in caches:
        caches[cache_name].clear()


@pytest.fixture
def mock_request_app() -> Callable[..., ContextManager]:
    """替换 APIGateway JWT 认证，仅向请求注入指定的调用方应用信息，权限类仍按真实逻辑判断"""

    def _mock(verified: bool = True, tenant_mode: str = "single", tenant_id: str = "") -> ContextManager:
        app = App(bk_app_code="test_app", verified=verified, tenant_mode=tenant_mode, tenant_id=tenant_id)

        class FakeAppAuthentication(BaseAuthentication):
            def authenticate(self, request):
                request.app = app
                # 与 ApiGatewayJWTAuthentication 一致，始终视为认证成功，由权限类决定是否放行
                return AnonymousUser(), None

        return mock.patch.object(OpenApiCommonMixin, "authentication_classes", [FakeAppAuthentication])

    return _mock


@pytest.fixture
def api_client(random_tenant, mock_request_app):
    with override_settings(ENABLE_MULTI_TENANT_MODE=True):
        client = APIClient()
        client.defaults["HTTP_X_BK_TENANT_ID"] = random_tenant.id
        with mock_request_app(tenant_id=random_tenant.id):
            yield client


@pytest.fixture
def _init_tenant_users_depts(random_tenant, full_local_data_source) -> None:
    """初始化租户部门 & 租户用户"""
    sync_users_depts_to_tenant(random_tenant, full_local_data_source)


@pytest.fixture
def _init_virtual_tenant_users(random_tenant, full_virtual_data_source) -> None:
    """初始化租户用户"""
    sync_users_depts_to_tenant(random_tenant, full_virtual_data_source)


@pytest.fixture
def tenant_common_variable(random_tenant) -> List[TenantCommonVariable]:
    property_1 = TenantCommonVariable.objects.create(tenant=random_tenant, name="key_1", value="value_1")
    property_2 = TenantCommonVariable.objects.create(tenant=random_tenant, name="key_2", value="value_2")
    return [property_1, property_2]
