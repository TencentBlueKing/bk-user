# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from typing import List

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.tenant.models import Tenant, TenantUser
from bkuser.biz.validators import (
    validate_data_source_user_username,
    validate_duplicate_tenant_name,
    validate_logo,
    validate_user_new_password,
)
from bkuser.common.serializers import StringArrayField


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
    enable_login = serializers.BooleanField(help_text="是否启用账密登录")


class TenantBuiltinManagerUpdateInputSLZ(serializers.Serializer):
    username = serializers.CharField(
        help_text="用户名", validators=[validate_data_source_user_username], required=False, allow_blank=True
    )
    enable_login = serializers.BooleanField(help_text="是否启用账密登录", required=False)


class TenantBuiltinManagerPasswordUpdateInputSLZ(serializers.Serializer):
    password = serializers.CharField(help_text="重置的新密码")

    def validate_password(self, password: str) -> str:
        return validate_user_new_password(
            password=password,
            data_source_user_id=self.context["data_source_user_id"],
            plugin_config=self.context["plugin_config"],
        )


class TenantRealManagerListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户ID", source="tenant_user.id")
    username = serializers.CharField(help_text="用户名", source="tenant_user.data_source_user.username")
    full_name = serializers.CharField(help_text="姓名", source="tenant_user.data_source_user.full_name")


class TenantRealManagerCreateInputSLZ(serializers.Serializer):
    ids = serializers.ListField(child=serializers.CharField(help_text="租户用户 ID"), allow_empty=False)

    def validate_ids(self, ids: List[str]) -> List[str]:
        if not ids:
            return []

        # 过滤出本租户、实名类型的 ID
        valid_ids = TenantUser.objects.filter(
            tenant_id=self.context["tenant_id"], data_source__type=DataSourceTypeEnum.REAL, id__in=ids
        ).values_list("id", flat=True)

        # 非法 ID
        if invalid_ids := set(ids) - set(valid_ids):
            raise ValidationError(_("非本租户实名账号（ids={}）不允许添加").format(invalid_ids))

        return ids


class TenantRealManagerDestroyInputSLZ(serializers.Serializer):
    ids = StringArrayField(help_text="租户用户 ID 列表，多个以英文逗号分隔")


class TenantRealUserListInputSLZ(serializers.Serializer):
    exclude_manager = serializers.BooleanField(
        help_text="是否排除管理员", required=False, allow_null=True, default=False
    )
    keyword = serializers.CharField(help_text="搜索关键字", required=False, allow_blank=True, default="")


class TenantRealUserListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户ID")
    username = serializers.CharField(help_text="用户名", source="data_source_user.username")
    full_name = serializers.CharField(help_text="姓名", source="data_source_user.full_name")
