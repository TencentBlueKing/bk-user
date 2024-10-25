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

from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.tenant import TenantUserHandler
from bkuser.common.validators import validate_phone_with_country_code


class SendVerificationCodeInputSLZ(serializers.Serializer):
    tenant_id = serializers.CharField(help_text="租户 ID")
    phone = serializers.CharField(help_text="手机号码")
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )

    def validate(self, attrs):
        try:
            validate_phone_with_country_code(phone=attrs["phone"], country_code=attrs["phone_country_code"])
        except ValueError as e:
            raise ValidationError(str(e))

        return attrs


class GenResetPasswordUrlByVerificationCodeInputSLZ(serializers.Serializer):
    tenant_id = serializers.CharField(help_text="租户 ID")
    phone = serializers.CharField(help_text="手机号码")
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )
    verification_code = serializers.CharField(help_text="验证码", max_length=32)

    def validate(self, attrs):
        try:
            validate_phone_with_country_code(phone=attrs["phone"], country_code=attrs["phone_country_code"])
        except ValueError as e:
            raise ValidationError(str(e))

        return attrs


class GenResetPasswordUrlByVerificationCodeOutputSLZ(serializers.Serializer):
    reset_password_url = serializers.CharField(help_text="密码重置链接")


class SendResetPasswordEmailInputSLZ(serializers.Serializer):
    tenant_id = serializers.CharField(help_text="租户 ID")
    email = serializers.EmailField(help_text="邮箱")


class ListUserByResetPasswordTokenInputSLZ(serializers.Serializer):
    token = serializers.CharField(help_text="密码重置 Token", max_length=255)


class TenantUserMatchedByTokenOutputSLZ(serializers.Serializer):
    tenant_user_id = serializers.CharField(help_text="租户用户 ID", source="id")
    username = serializers.CharField(help_text="用户名", source="data_source_user.username")
    display_name = serializers.SerializerMethodField(help_text="展示用名称")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)


class ResetPasswordByTokenInputSLZ(serializers.Serializer):
    tenant_user_id = serializers.CharField(help_text="租户用户 ID")
    password = serializers.CharField(help_text="新密码")
    token = serializers.CharField(help_text="密码重置 Token", max_length=255)
