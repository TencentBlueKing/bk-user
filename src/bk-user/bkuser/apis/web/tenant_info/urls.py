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
    # 租户基本信息
    path("", views.TenantRetrieveUpdateApi.as_view(), name="tenant_info.retrieve_update"),
    # 租户内置管理账号
    path(
        "builtin-manager/",
        views.TenantBuiltinManagerRetrieveUpdateApi.as_view(),
        name="tenant_info.retrieve_update_builtin_manager",
    ),
    path(
        "builtin-manager/password/",
        views.TenantBuiltinManagerPasswordUpdateApi.as_view(),
        name="tenant_info.update_builtin_manager_password",
    ),
    # 租户实名管理员
    path(
        "real-managers/",
        views.TenantRealManagerListUpdateApi.as_view(),
        name="tenant_info.list_update_real_manager",
    ),
    path("real-users/", views.TenantRealUserListApi.as_view(), name="tenant_info.list_tenant_real_user"),
]
