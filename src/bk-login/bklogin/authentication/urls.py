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
from django.urls import path
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    # 登录入口
    path("", views.LoginView.as_view()),
    # 登录小窗入口
    path("plain/", xframe_options_exempt(views.LoginView.as_view())),
    # 前端页面（选择登录的用户）
    path("page/users/", TemplateView.as_view(template_name="index.html"), name="page.users"),
    # ------------------------------------------ 租户 & 登录方式选择 ------------------------------------------
    # 租户信息
    path("tenants/", views.TenantListApi.as_view()),
    # 认证源
    path(
        "tenants/<str:tenant_id>/idp-owner-tenants/<str:idp_owner_tenant_id>/idps/", views.TenantIdpListApi.as_view()
    ),
    # ------------------------------------------ 认证插件 ------------------------------------------
    # 插件认证
    path(
        "tenants/<str:tenant_id>/idps/<str:idp_id>/actions/<str:action>/",
        xframe_options_exempt(views.IdpPluginDispatchView.as_view()),
    ),
    path("auth/idps/<str:idp_id>/actions/<str:action>/", xframe_options_exempt(views.IdpPluginDispatchView.as_view())),
    # ------------------------------------------ 用户选择 ------------------------------------------
    # 已认证后的用户列表
    path("tenant-users/", views.TenantUserListApi.as_view()),
    # 确认登录的用户
    path("sign-in-users/", views.SignInTenantUserCreateApi.as_view()),
]
