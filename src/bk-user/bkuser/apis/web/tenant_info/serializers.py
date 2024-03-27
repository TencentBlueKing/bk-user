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
from django.conf import settings
from rest_framework import serializers

from bkuser.apps.tenant.models import Tenant
from bkuser.biz.validators import (
    validate_data_source_user_username,
    validate_duplicate_tenant_name,
    validate_logo,
    validate_user_new_password,
)


class TenantRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名")
    logo = serializers.SerializerMethodField(help_text="租户 Logo")
    visible = serializers.BooleanField(help_text="租户可见性")
    user_number_visible = serializers.BooleanField(help_text="人员数量是否可见")

    def get_logo(self, obj: Tenant) -> str:
        return obj.logo or settings.DEFAULT_TENANT_LOGO


class TenantUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.CharField(
        help_text="租户 Logo",
        required=False,
        allow_blank=True,
        default=settings.DEFAULT_TENANT_LOGO,
        validators=[validate_logo],
    )
    visible = serializers.BooleanField(help_text="租户可见性")
    user_number_visible = serializers.BooleanField(help_text="人员数量是否可见")

    def validate_name(self, name: str) -> str:
        return validate_duplicate_tenant_name(name, self.context["tenant_id"])


class TenantBuiltinManagerRetrieveOutputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="用户名")
    enable_account_password_login = serializers.BooleanField(help_text="是否启用账密登录")


class TenantBuiltinManagerUpdateInputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="用户名", validators=[validate_data_source_user_username])
    enable_account_password_login = serializers.BooleanField(help_text="是否启用账密登录")


class TenantBuiltinManagerPasswordUpdateInputSLZ(serializers.Serializer):
    password = serializers.CharField(help_text="重置的新密码")

    def validate_password(self, password: str) -> str:
        return validate_user_new_password(
            password=password,
            data_source_user_id=self.context["data_source_user_id"],
            plugin_config=self.context["plugin_config"],
        )
