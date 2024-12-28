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
from django.urls import path

from . import views
from .compatibility import views as compatibility_views

urlpatterns = [
    # 兼容 API, 兼容原有通过 ESB 和直接调用的两种方式
    path("accounts/is_login/", compatibility_views.TokenIntrospectCompatibilityApi.as_view(api_version="v1")),
    path("accounts/get_user/", compatibility_views.UserRetrieveCompatibilityApi.as_view(api_version="v1")),
    path("api/v2/is_login/", compatibility_views.TokenIntrospectCompatibilityApi.as_view(api_version="v2")),
    path("api/v2/get_user/", compatibility_views.UserRetrieveCompatibilityApi.as_view(api_version="v2")),
    path("api/v3/is_login/", compatibility_views.TokenIntrospectCompatibilityApi.as_view(api_version="v3")),
    path("api/v3/get_user/", compatibility_views.UserRetrieveCompatibilityApi.as_view(api_version="v3")),
    # Note: 新的 OpenAPI 后面统一接入 APIGateway，不支持直接调用
    # 通用 OpenAPI
    path("api/v3/open/bk-tokens/verify/", views.TokenVerifyApi.as_view(), name="v3_open.bk_token.verify"),
    path(
        "api/v3/open/bk-tokens/userinfo/",
        views.TokenUserInfoRetrieveApi.as_view(),
        name="v3_open.bk_token.userinfo_retrieve",
    ),
    # 提供给 apigw 的内部 API
    path(
        "api/v3/apigw/bk-tokens/verify/", views.TokenVerifyApiByBearerAuth.as_view(), name="v3_apigw.bk_token.verify"
    ),
    # 提供给 bkuser 的内部 API
    path(
        "api/v3/bkuser/bk-tokens/userinfo/",
        views.TokenUserInfoRetrieveApiByBkUserAppAuth.as_view(),
        name="v3_bkuser.bk_token.userinfo_retrieve",
    ),
]
