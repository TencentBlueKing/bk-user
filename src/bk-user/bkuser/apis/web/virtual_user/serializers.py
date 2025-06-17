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
from typing import List

from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.models import TenantUser, VirtualUserAppRelation, VirtualUserOwnerRelation
from bkuser.biz.validators import validate_data_source_user_username


def _validate_duplicate_data_source_username(data_source_id: str, username: str, data_source_user_id: int = 0) -> str:
    """校验数据源用户名是否重复"""
    queryset = DataSourceUser.objects.filter(data_source_id=data_source_id, username=username)
    # 过滤掉自身
    if data_source_user_id:
        queryset = queryset.exclude(id=data_source_user_id)

    if queryset.exists():
        raise ValidationError(_("用户名 {} 已存在").format(username))

    return username


def _validate_owners(owners: List[str]) -> List[str]:
    """
    校验责任人列表
    1. 去重
    2. 检查每个责任人是否存在且为实体用户
    """
    found_owners = set(
        TenantUser.objects.filter(id__in=owners, data_source__type=DataSourceTypeEnum.REAL).values_list(
            "id", flat=True
        )
    )
    if invalid_owners := set(owners) - found_owners:
        raise ValidationError(_("用户 {} 不存在或不是实体用户").format(invalid_owners))

    return owners


class VirtualUserListInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", required=False, allow_blank=True, default="")


class VirtualUserListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.CharField(help_text="用户名", source="data_source_user.username")
    full_name = serializers.CharField(help_text="姓名", source="data_source_user.full_name")
    app_codes = serializers.SerializerMethodField(help_text="应用编码列表")
    owners = serializers.SerializerMethodField(help_text="责任人列表")

    @swagger_serializer_method(serializer_or_field=serializers.ListField(child=serializers.CharField()))
    def get_app_codes(self, obj: TenantUser) -> List[str]:
        return self.context["app_code_map"][obj.id]

    @swagger_serializer_method(serializer_or_field=serializers.ListField(child=serializers.CharField()))
    def get_owners(self, obj: TenantUser) -> List[str]:
        return self.context["owner_map"][obj.id]


class VirtualUserCreateInputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="用户名", validators=[validate_data_source_user_username])
    full_name = serializers.CharField(help_text="姓名")
    app_codes = serializers.ListField(help_text="应用编码列表", child=serializers.CharField())
    owners = serializers.ListField(help_text="责任人列表", child=serializers.CharField())

    def validate_username(self, username: str) -> str:
        return _validate_duplicate_data_source_username(self.context["data_source_id"], username)

    def validate_app_codes(self, app_codes: List[str]) -> List[str]:
        # 过滤重复值
        return list(set(app_codes))

    def validate_owners(self, owners: List[str]) -> List[str]:
        return _validate_owners(owners)


class VirtualUserCreateOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")


class VirtualUserRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.CharField(help_text="用户名", source="data_source_user.username")
    full_name = serializers.CharField(help_text="姓名", source="data_source_user.full_name")
    app_codes = serializers.SerializerMethodField(help_text="应用编码列表")
    owners = serializers.SerializerMethodField(help_text="责任人列表")

    @swagger_serializer_method(serializer_or_field=serializers.ListField(child=serializers.CharField()))
    def get_app_codes(self, obj: TenantUser) -> List[str]:
        return list(VirtualUserAppRelation.objects.filter(tenant_user=obj).values_list("app_code", flat=True))

    @swagger_serializer_method(serializer_or_field=serializers.ListField(child=serializers.CharField()))
    def get_owners(self, obj: TenantUser) -> List[str]:
        return list(VirtualUserOwnerRelation.objects.filter(tenant_user=obj).values_list("owner_id", flat=True))


class VirtualUserUpdateInputSLZ(serializers.Serializer):
    full_name = serializers.CharField(help_text="姓名")
    app_codes = serializers.ListField(help_text="应用编码列表", child=serializers.CharField())
    owners = serializers.ListField(help_text="责任人列表", child=serializers.CharField())

    def validate_app_codes(self, app_codes: List[str]) -> List[str]:
        # 过滤重复值
        return list(set(app_codes))

    def validate_owners(self, owners: List[str]) -> List[str]:
        return _validate_owners(owners)
