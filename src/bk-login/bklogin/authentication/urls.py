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
from django.urls import path
from django.views.decorators.clickjacking import xframe_options_exempt

from . import views

urlpatterns = [
    # 登录入口
    path("", views.LoginView.as_view()),
    # 登录小窗入口
    path("plain/", xframe_options_exempt(views.LoginView.as_view())),
    # 前端页面（选择登录的用户）
    path("page/users/", views.PageUserView.as_view(), name="page.users"),
    # ------------------------------------------ 通用配置 ------------------------------------------
    # 通用配置
    path("global-settings/", views.GlobalSettingRetrieveApi.as_view()),
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
