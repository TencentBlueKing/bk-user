# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
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
        "tenant-users/<str:id>/",
        views.TenantUserRetrieveApi.as_view(),
        name="personal_center.tenant_users.retrieve",
    ),
    path(
        "tenant-users/<str:id>/logo/",
        views.TenantUserLogoUpdateApi.as_view(),
        name="personal_center.tenant_users.logo.update",
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
    path(
        "tenant-users/<str:id>/language/",
        views.TenantUserLanguageUpdateApi.as_view(),
        name="personal_center.tenant_users.language.update",
    ),
    path(
        "tenant-users/<str:id>/time-zone/",
        views.TenantUserTimeZoneUpdateApi.as_view(),
        name="personal_center.tenant_users.time_zone.update",
    ),
    path(
        "tenant-users/<str:id>/extras/",
        views.TenantUserExtrasUpdateApi.as_view(),
        name="personal_center.tenant_users.extras.update",
    ),
    path(
        "tenant-users/<str:id>/fields/",
        views.TenantUserFieldListApi.as_view(),
        name="personal_center.tenant_users.fields.list",
    ),
    path(
        "tenant-users/<str:id>/feature-flags/",
        views.TenantUserFeatureFlagListApi.as_view(),
        name="personal_center.tenant_users.feature_flag.list",
    ),
    path(
        "tenant-users/<str:id>/password/",
        views.TenantUserPasswordUpdateApi.as_view(),
        name="personal_center.tenant_users.password.update",
    ),
    path(
        "tenant-users/<str:id>/phone-verification-code/",
        views.TenantUserPhoneVerificationCodeSendApi.as_view(),
        name="personal_center.tenant_users.phone_verification_code.send",
    ),
    path(
        "tenant-users/<str:id>/email-verification-code/",
        views.TenantUserEmailVerificationCodeSendApi.as_view(),
        name="personal_center.tenant_users.email_verification_code.send",
    ),
]
