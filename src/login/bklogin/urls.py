# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS
Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.conf import settings
from django.conf.urls import include, url
from django.http import HttpResponse
from django.views import i18n as django_i18n_views
from django.views.i18n import JavaScriptCatalog

from bklogin.api import views as views_api
from bklogin.bkauth import views as auth_views
from bklogin.healthz import views as healthz_views

urlpatterns = [
    # 登录页面
    url(r"^$", auth_views.LoginView.as_view()),
    # 登录弹窗
    url(r"^plain/$", auth_views.LoginView.as_view(is_plain=True)),
    url(r"^logout/$", auth_views.LogoutView.as_view()),
    # ========================= the apis =========================
    # NOTE: 所有get_all_user/get_batch_user api应该直接调用usermgr的esb接口或者后台接口, 不应该走login
    # please use api get_all_user/get_batch_user via esb, should not from login directly
    # FIXME: move into api/urls.py => check v1/v2/v3 is called or not?
    # FIXME: remove /login/api/v[1,2,3]/ ?
    url(
        r"^accounts/",
        include(
            [
                url(r"^is_login/$", views_api.CheckLoginView.as_view()),
                url(r"^get_user/$", views_api.UserView.as_view()),
            ]
        ),
    ),
    # 登录态验证接口保持与后台一致
    url(
        r"^login/accounts/",
        include(
            [
                url(r"^is_login/$", views_api.CheckLoginView.as_view()),
                url(r"^get_user/$", views_api.UserView.as_view()),
            ]
        ),
    ),
    # 登陆模块 API，V2，线上
    url(
        r"^api/v2/",
        include(
            [
                url(r"^is_login/$", views_api.CheckLoginViewV2.as_view()),
                url(r"^get_user/$", views_api.UserViewV2.as_view()),
            ]
        ),
    ),
    # 登陆模块 API，V2，本地
    url(
        r"^login/api/v2/",
        include(
            [
                url(r"^is_login/$", views_api.CheckLoginViewV2.as_view()),
                url(r"^get_user/$", views_api.UserViewV2.as_view()),
            ]
        ),
    ),
    # 登陆模块 API，V3，线上
    url(
        r"^api/v3/",
        include(
            [
                url(r"^is_login/$", views_api.CheckLoginViewV3.as_view()),
                url(r"^get_user/$", views_api.UserViewV3.as_view()),
            ]
        ),
    ),
    # 登陆模块 API，V3，本地
    url(
        r"^login/api/v3/",
        include(
            [
                url(r"^is_login/$", views_api.CheckLoginViewV3.as_view()),
                url(r"^get_user/$", views_api.UserViewV3.as_view()),
            ]
        ),
    ),
    # ========================= the apis =========================
    # 连通性检查
    url(r"^ping/$", healthz_views.ping),
    # 检查统一登录是否正常运行
    url(r"^healthz/", healthz_views.healthz),
    # 反搜索
    url(r"^robots\.txt$", lambda r: HttpResponse("User-agent: *\nDisallow: /", content_type="text/plain")),
    # prometheus metrics
    url(r"", include("django_prometheus.urls")),
    # ========================= i18n =========================
    # 无登录态下切换语言
    url(r"^i18n/setlang/$", django_i18n_views.set_language, name="set_language"),
    # 处理JS翻译
    url(r"^jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
]

from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # noqa

urlpatterns += staticfiles_urlpatterns()

# 启用IAM，配置回调地址
if settings.ENABLE_IAM:
    from bklogin.bkiam.resource_providers import dispatcher

    # IAM 回调资源
    urlpatterns += [
        url(r'^api/v1/iam/resource/$', dispatcher.as_view()),
    ]
