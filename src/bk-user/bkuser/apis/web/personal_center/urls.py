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
    # 关联用户列表
    path(
        "current-natural-user/",
        views.NaturalUserTenantUserListApi.as_view(),
        name="personal_center.current_natural_user",
    ),
    # 租户用户详情
    path(
        "tenant-users/<str:id>/", views.TenantUserRetrieveApi.as_view(), name="personal_center.tenant_users.retrieve"
    ),
    path(
        "tenant-users/<str:id>/phone/",
        views.TenantUserPhoneUpdateApi.as_view(),
        name="personal_center.tenant_users.phone.update",
    ),
    path(
        "tenant-users/<str:id>/email/",
        views.TenantUserEmailUpdateApi.as_view(),
        name="personal_center.tenant_users.email.update",
    ),
]
