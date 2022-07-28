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
from django.conf import settings
from rest_framework.test import APIRequestFactory

from bkuser_core.common.http import _force_response_data, force_response_ee_format, force_response_raw_format
from bkuser_core.profiles.v2.views import ProfileViewSet

pytestmark = pytest.mark.django_db


class TestResponseFormat:
    @pytest.fixture(scope="class")
    def factory(self):
        return APIRequestFactory(
            enforce_csrf_checks=False,
            **{
                "HTTP_FORCE_RAW_RESPONSE": False,
                "HTTP_RAW_USERNAME": True,
                "Content-Type": "application/json",
                "HTTP_AUTHORIZATION": f"iBearer {list(settings.INTERNAL_AUTH_TOKENS.keys())[0]}",
            },
        )

    @pytest.fixture(scope="class")
    def p_request(self, factory):
        return factory.get("/api/v2/profiles/")

    @pytest.fixture(scope="class")
    def view(self):
        return ProfileViewSet.as_view({"get": "list", "post": "create"})

    def test_raw_force_to_ee(self, view, p_request):
        """测试原生转换企业版"""
        response = view(request=p_request)
        _resp = force_response_ee_format(response)
        assert _resp.data.get("result")
        assert _resp.data.get("message")

    @pytest.mark.django_db
    def test_raw_force_to_ee_cache(self, view, p_request):
        """测试原生转换企业版"""
        response = view(request=p_request)
        response._post_render_callbacks = None

        _resp = force_response_ee_format(response)
        assert _resp.data.get("result")
        assert _resp.data.get("message")

    def test_ee_force_to_raw(self, view, p_request):
        """测试企业版转换原生"""
        response = view(request=p_request)
        response = _force_response_data(response, {"test": "test"})

        _resp = force_response_raw_format(response)
        assert not _resp.data.get("result")
        assert not _resp.data.get("message")

    def test_ee_force_to_raw_cache(self, view, p_request):
        """测试企业版转换原生缓存"""
        response = view(request=p_request)
        response = _force_response_data(response, {"test": "test"})
        response._post_render_callbacks = None

        _resp = force_response_raw_format(response)
        assert not _resp.data.get("result")
        assert not _resp.data.get("message")

    def test_none_data(self, view, p_request):
        """测试空data"""
        response = view(request=p_request)
        response = _force_response_data(response, None)
        response._post_render_callbacks = None

        _resp = force_response_ee_format(response)
        assert _resp.data.get("result")
        assert _resp.data.get("message")
        assert _resp.data.get("data") is None

        _resp = force_response_raw_format(response)
        assert _resp.data is None
