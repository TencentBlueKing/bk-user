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
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, re_path
from django.views.generic.base import RedirectView
from django.views.i18n import JavaScriptCatalog

from bkuser_shell.proxy.views import WebPageViewSet

urlpatterns = [
    re_path(r"^", include("bkuser_shell.account.urls")),
    re_path("", include("bkuser_shell.proxy.urls")),
    # TODO: version should be change to a different impl
    re_path(r"^", include("bkuser_shell.version_log.urls")),
    re_path(
        r"^favicon.ico$",
        RedirectView.as_view(url=staticfiles_storage.url("img/favicon.ico")),
    ),
    re_path(
        r"^jsi18n/(?P<packages>\S+?)/$",
        JavaScriptCatalog.as_view(),
        name="javascript-catalog",
    ),
    re_path(r"^", include("django_prometheus.urls")),
]

# 当且仅当前端独立部署时托管 STATIC_URL 路由
if settings.IS_PAGES_INDEPENDENT_DEPLOYMENT:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 其余path交由前端处理
urlpatterns += [
    re_path(r"^login_success/", WebPageViewSet.as_view({"get": "login_success"}), name="login_success"),
    re_path(r"^", WebPageViewSet.as_view({"get": "index"}), name="index"),
]
