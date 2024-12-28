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
from bklogin.common.error_codes import error_codes


class APIGatewayAppVerifiedMixin:
    """校验来源 APIGateway JWT 的应用是否认证"""

    def dispatch(self, request, *args, **kwargs):  # type: ignore
        app = getattr(request, "app", None)
        if app and app.verified:
            return super().dispatch(request, *args, **kwargs)  # type: ignore

        raise error_codes.UNAUTHENTICATED.f("the api must be verify app from api gateway")


class InnerBearerTokenVerifiedMixin:
    """校验来源内部请求的 Bearer Token 是否认证"""

    def dispatch(self, request, *args, **kwargs):
        token = getattr(request, "inner_bearer_token", None)
        if token and token.verified:
            return super().dispatch(request, *args, **kwargs)  # type: ignore

        raise error_codes.UNAUTHENTICATED.f("the api must be verify inner bearer token")


class BkUserAppVerifiedMixin:
    """校验来源内部 Bk User App 的请求"""

    def dispatch(self, request, *args, **kwargs):
        bk_user_app_verified = getattr(request, "bk_user_app_verified", False)
        if bk_user_app_verified:
            return super().dispatch(request, *args, **kwargs)  # type: ignore

        raise error_codes.UNAUTHENTICATED.f("the api must be verify from bk user app")
