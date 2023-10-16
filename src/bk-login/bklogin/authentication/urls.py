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

from . import views

urlpatterns = [
    path("", views.LoginView.as_view()),
    # 租户配置
    path("tenant-global-settings/", views.TenantGlobalSettingRetrieveApi.as_view()),
    # 租户信息
    path("tenants/", views.TenantListApi.as_view()),
    path("tenants/<str:tenant_id>/", views.TenantRetrieveApi.as_view()),
    # 确认登录的租户
    path("sign-in-tenants/", views.SignInTenantCreateApi.as_view()),
    # 认证源
    path("idps/", views.TenantIdpListApi.as_view()),
    # 已认证后的用户
    path("tenant-users/", views.TenantUserListApi.as_view()),
    # 确认登录的用户
    path("sign-in-users/", views.SignInTenantUserCreateApi.as_view()),
    # Test
    path("index/", views.IndexView.as_view()),
    # API
    path("api/v1/is_login/", views.CheckTokenApi.as_view()),
    path("api/v1/get_user/", views.GetUserApi.as_view()),
]

urlpatterns += [
    # 各种认证
    path("auth/idps/<str:idp_id>/actions/<str:action>/", views.IdpPluginDispatchView.as_view()),
]
