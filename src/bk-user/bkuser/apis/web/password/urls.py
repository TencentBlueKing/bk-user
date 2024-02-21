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

from bkuser.apis.web.password import views

# 忘记密码交互设计：
#   - 通过邮箱重置：
#       - 发送重置密码链接到邮箱
#       - 用户访问密码重置链接
#       - 选择要重置的租户用户
#       - 输入新密码（含确认）并提交
#   - 通过手机号码重置：
#       - 发送验证码到手机
#       - 用户输入验证码，验证正确后跳转到密码重置链接
#       - 选择要重置的租户用户
#       - 输入新密码（含确认）并提交

urlpatterns = [
    # 发送重置密码验证码到手机
    path(
        "send-verification-code-to-phone/",
        views.SendResetPasswordVerificationCodeApi.as_view(),
        name="password.send_verification_code",
    ),
    # 通过验证码获取密码重置链接
    path(
        "get-passwd-reset-url-by-verification-code/",
        views.GetResetPasswordUrlByVerificationCodeApi.as_view(),
        name="password.get_passwd_reset_url_by_verification_code",
    ),
    # 发送密码重置链接到邮箱
    path(
        "send-passwd-reset-url-to-email/",
        views.SendResetPasswordUrlToEmailApi.as_view(),
        name="password.send_passwd_reset_url_to_email",
    ),
    # 通过密码重置 Token 获取可选租户用户
    path(
        "list-user-by-passwd-reset-token/",
        views.ListUserByResetPasswordTokenApi.as_view(),
        name="password.list_user_by_passwd_reset_token",
    ),
    # 通过密码重置 Token 重置密码
    path(
        "reset-by-passwd-reset-token/",
        views.ResetPasswordByTokenApi.as_view(),
        name="password.reset_by_passwd_reset_token",
    ),
]
