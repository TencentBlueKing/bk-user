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
    # 本地用户身份凭据校验
    path(
        "local-user-credentials/authenticate/",
        views.LocalUserCredentialAuthenticateApi.as_view(),
        name="login.local_user_credentials.authenticate",
    ),
    # 全局配置
    path("global-settings/", views.GlobalSettingRetrieveApi.as_view(), name="login.global_setting.retrieve"),
    # 租户列表
    path("tenants/", views.TenantListApi.as_view(), name="login.tenant.list"),
    # 单个租户
    path("tenants/<str:id>/", views.TenantRetrieveApi.as_view(), name="login.tenant.retrieve"),
    # 获取租户的认证源列表
    path("tenants/<str:tenant_id>/idps/", views.IdpListApi.as_view(), name="login.idp.list"),
    # 单个认证源
    path("idps/<str:id>/", views.IdpRetrieveApi.as_view(), name="login.idp.retrieve"),
    # 认证源匹配用户
    path(
        "tenants/<str:tenant_id>/idps/<str:idp_id>/matched-tenant-users/",
        views.TenantUserMatchApi.as_view(),
        name="login.matched_tenant_user.match",
    ),
    # 查询租户用户
    path("tenant-users/<str:id>/", views.TenantUserRetrieveApi.as_view(), name="login.tenant_user.retrieve"),
]
