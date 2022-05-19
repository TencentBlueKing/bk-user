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
import json

import pytest

from bkuser_core.common.middlewares import MethodOverrideMiddleware
from bkuser_core.tests.apis.utils import get_api_factory


class TestMethodOverrideMW:
    @pytest.fixture()
    def factory(self):
        return get_api_factory({"HTTP_X_HTTP_METHOD_OVERRIDE": "GET"})

    @pytest.mark.parametrize(
        "post_data",
        [
            {"username": "test_name", "password": "test_pwd"},
            {"age": 33, "gender": "female"},
            {"exact_lookups": ["aa", "bb", "cc"]},
        ],
    )
    def test_process_request(self, factory, post_data):
        request = factory.post("/", data=post_data)
        request._body = json.dumps(post_data)

        method_override_middleware = MethodOverrideMiddleware()
        method_override_middleware.process_request(request)

        assert request.method == request.META["HTTP_X_HTTP_METHOD_OVERRIDE"]
        assert request.GET.dict() == post_data
