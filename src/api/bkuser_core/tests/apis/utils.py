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
from django.conf import settings
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory


def get_api_factory(force_params: dict = None):
    """获取一个通用的 ApiFactory"""
    force_params = force_params or {}
    normal_params = {
        "HTTP_FORCE_RAW_RESPONSE": True,
        "Content-Type": "application/json",
        "HTTP_X_BKUSER_OPERATOR": "tester",
        # "HTTP_RAW_USERNAME": True,
        # should be removed after enhanced_account removed the token auth
        "HTTP_AUTHORIZATION": f"iBearer {list(settings.INTERNAL_AUTH_TOKENS.keys())[0]}",
    }
    normal_params.update(force_params)

    return APIRequestFactory(
        enforce_csrf_checks=False,
        **normal_params,
    )


def make_request_operator_aware(request: Request, operator: str):
    """给 request 添加 operator"""
    setattr(request, "operator", operator)
    return request
