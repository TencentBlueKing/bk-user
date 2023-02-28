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
from django.conf.urls import include, url
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title="蓝鲸用户管理 API",
        default_version="v2",
        description="蓝鲸用户管理后台服务 API",
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=CustomOpenAPISchemaGenerator,
    patterns=[
        url(r"^", include("bkuser_core.monitoring.urls")),
        url(r"^", include("bkuser_core.departments.urls")),
        url(r"^", include("bkuser_core.profiles.urls")),
        url(r"^", include("bkuser_core.categories.urls")),
        # url(r"^", include("bkuser_core.user_settings.urls")),
        # url(r"^", include("bkuser_core.audit.urls")),
    ],
)

urlpatterns = []
if settings.DEBUG:
    urlpatterns += [
        url(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
        url(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
        url(r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    ]
