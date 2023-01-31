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

from django.urls.conf import path, re_path

from .views import CommonProxyNoAuthViewSet, CommonProxyViewSet, HealthzViewSet, LoginInfoViewSet
from bkuser_shell.version_log.views import VersionLogListViewSet

urlpatterns = [
    # common
    path(
        "api/v1/web/site/footer/",
        CommonProxyNoAuthViewSet.as_view({"get": "request"}),
        name="common.no_auth.proxy.1",
    ),
    path(
        "api/v1/web/passwords/reset/send_email/",
        CommonProxyNoAuthViewSet.as_view({"post": "request"}),
        name="common.no_auth.proxy.2",
    ),
    path(
        "api/v1/web/passwords/reset/by_token/",
        CommonProxyNoAuthViewSet.as_view({"post": "request"}),
        name="common.no_auth.proxy.3",
    ),
    path(
        "api/v1/web/passwords/settings/by_token/",
        CommonProxyNoAuthViewSet.as_view({"get": "request"}),
        name="common.no_auth.proxy.4",
    ),
    path(
        "api/v1/web/passwords/reset/verification_code/send_sms/",
        CommonProxyNoAuthViewSet.as_view({"post": "request"}),
        name="common.no_auth.proxy.5",
    ),
    path(
        "api/v1/web/passwords/reset/verification_code/verify/",
        CommonProxyNoAuthViewSet.as_view({"post": "request"}),
        name="common.no_auth.proxy.6",
    ),
    # NOTE: 前端暂时切换成这个
    path(
        "api/v1/web/version_logs/",
        VersionLogListViewSet.as_view(),
        name="version_log_list",
    ),
    path("api/v1/web/profiles/me/", LoginInfoViewSet.as_view({"get": "get"}), name="profiles.login_info.v1"),
    re_path(
        "^api/v1/web/.+$",
        CommonProxyViewSet.as_view(
            {"get": "request", "post": "request", "delete": "request", "put": "request", "patch": "request"}
        ),
        name="common.proxy",
    ),
    # healthz
    path("healthz/", HealthzViewSet.as_view({"get": "list"}), name="healthz"),
    path("ping/", HealthzViewSet.as_view({"get": "pong"}), name="pong"),
]
