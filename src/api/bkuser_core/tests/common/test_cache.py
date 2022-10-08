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

# from bkuser_core.common.http import _force_response_data
from bkuser_core.profiles.v2.views import ProfileViewSet
from bkuser_core.tests.apis.utils import get_api_factory

pytestmark = pytest.mark.django_db


class TestCache:
    def test_exclude_header_cache(self):
        # cached_factory = get_api_factory({"HTTP_FORCE_RAW_RESPONSE": True})
        # cached_request = cached_factory.get("/api/v2/profiles/")
        # cached_view = ProfileViewSet.as_view({"get": "list", "post": "create"})

        # 生成缓存
        # cached_response = cached_view(request=cached_request)
        # cached_response = _force_response_data(cached_response, {"test": "test"})
        # assert cached_response.data == {"test": "test"}

        no_cache_factory = get_api_factory({settings.FORCE_JSONP_HEADER: True})
        no_cache_request = no_cache_factory.get("/api/v2/profiles/")
        no_cache_view = ProfileViewSet.as_view({"get": "list", "post": "create"})
        no_cache_response = no_cache_view(request=no_cache_request)

        data = no_cache_response.data["results"]
        assert len(data) == 1
        assert data[0]["username"] == "admin"

        cache_again_factory = get_api_factory({settings.FORCE_JSONP_HEADER: False})
        cache_again_request = cache_again_factory.get("/api/v2/profiles/")
        cache_again_view = ProfileViewSet.as_view({"get": "list", "post": "create"})
        cache_again_response = cache_again_view(request=cache_again_request)

        if not settings.USE_DUMMY_CACHE_FOR_TEST:
            # 缓存开启的情况
            assert cache_again_response.data == {"test": "test"}
        else:
            assert len(cache_again_response.data["results"]) == 1
            assert cache_again_response.data["results"][0]["username"] == "admin"
