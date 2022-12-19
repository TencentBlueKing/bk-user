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

from django.urls.conf import path

from . import views

urlpatterns = [
    path(
        "reset/send_email/",
        views.PasswordResetSendEmailApi.as_view(),
        name="password.reset.sent_email",
    ),
    path(
        "reset/verification_code/send_sms/",
        views.PasswordResetSendVerificationCodeApi.as_view(),
        name="password.reset.sent_verification_code_sms",
    ),
    path(
        "reset/verification_code/verify/",
        views.PasswordVerifyVerificationCodeApi.as_view(),
        name="password.reset.verify_verification_code",
    ),
    path(
        "reset/by_token/",
        views.PasswordResetByTokenApi.as_view(),
        name="password.reset.by_token",
    ),
    path(
        "modify/",
        views.PasswordModifyApi.as_view(),
        name="password.modify",
    ),
    path(
        "settings/by_token/",
        views.PasswordListSettingsByTokenApi.as_view(),
        name="password.get_settings.by_token",
    ),
]
