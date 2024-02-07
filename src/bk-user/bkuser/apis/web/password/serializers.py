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
from typing import Dict

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class SendResetPasswordVerificationCodeInputSLZ(serializers.Serializer):
    tenant_id = serializers.CharField(help_text="租户 ID")
    email = serializers.CharField(help_text="邮箱", required=False)
    phone = serializers.CharField(help_text="手机号码", required=False)
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )

    def validate(self, attrs: Dict[str, str]) -> Dict[str, str]:
        if not (attrs.get("email") or attrs.get("phone")):
            raise serializers.ValidationError(_("必须提供邮箱或手机号码中的一项"))

        return attrs


class SendResetPasswordVerificationCodeOutputSLZ(serializers.Serializer):
    user_id = serializers.CharField(help_text="租户用户 ID")


class ResetPasswordByVerificationCodeInputSLZ(serializers.Serializer):
    user_id = serializers.CharField(help_text="租户用户 ID")
    verification_code = serializers.CharField(help_text="验证码")
