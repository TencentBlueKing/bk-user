# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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

from django.conf import settings
from django.conf.urls import re_path
from django.urls import include, path
from django.views.decorators.cache import never_cache
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from bkuser.common.views import VueTemplateView

urlpatterns = [
    # 产品功能API
    path("api/v3/web/", include("bkuser.apis.web.urls")),
    # 提供给登录服务使用的内部 API
    path("api/v3/login/", include("bkuser.apis.login.urls")),
    # 兼容旧版本用户管理 OpenAPI
    # Q: 这里使用 api/v1、api/v2 而非 api/v1/open、api/v2/open
    # A: 为了保证 ESB 调用的兼容，只需修改 ESB 配置 bk_user host，不需要依赖 ESB 的版本发布
    path("api/v1/", include("bkuser.apis.open_v1.urls")),
    path("api/v2/", include("bkuser.apis.open_v2.urls")),
    # 用于监控相关的，比如ping/healthz/sentry/metrics/otel等等
    path("", include("bkuser.monitoring.urls")),
]

# 蓝鲸通知中心
if settings.ENABLE_BK_NOTICE:
    urlpatterns += [
        path("api/v3/web/notices/", include(("bk_notice_sdk.urls", "notice"), namespace="notice")),
    ]

# swagger doc
if settings.SWAGGER_ENABLE:
    schema_view = get_schema_view(
        openapi.Info(
            title="BK-User API",
            default_version="vx",
            description="BK-User API Document",
            terms_of_service="http://bk-user.bking.com",
            contact=openapi.Contact(email="blueking@tencent.com"),
            license=openapi.License(name="BSD License"),
        ),
        public=False,
        permission_classes=[permissions.IsAuthenticated],
    )
    urlpatterns += [
        path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
        path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
        path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    ]


# static file
urlpatterns += [
    re_path("", never_cache(VueTemplateView.as_view())),
]
