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
from typing import Any, Dict, List

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.validators import validate_data_source_user_username
from bkuser.common.validators import validate_phone_with_country_code


class VirtualUserListInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", required=False, allow_blank=True, default="")


class VirtualUserListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.CharField(help_text="用户名", source="data_source_user.username")
    full_name = serializers.CharField(help_text="姓名", source="data_source_user.full_name")
    app_codes = serializers.SerializerMethodField(help_text="应用编码列表")
    owners = serializers.SerializerMethodField(help_text="责任人列表")
    # Note: 这里并不获取租户用户的联系方式，因为虚拟账号并不是同步而来，也无法通过登录后修改
    email = serializers.CharField(help_text="邮箱", source="data_source_user.email")
    phone = serializers.CharField(help_text="手机号", source="data_source_user.phone")
    phone_country_code = serializers.CharField(help_text="手机国际区号", source="data_source_user.phone_country_code")

    @swagger_serializer_method(serializer_or_field=serializers.ListField(child=serializers.CharField()))
    def get_app_codes(self, obj: TenantUser) -> List[str]:
        return [r.app_code for r in getattr(obj, "_prefetched_app_relations", [])]

    @swagger_serializer_method(serializer_or_field=serializers.ListField(child=serializers.CharField()))
    def get_owners(self, obj: TenantUser) -> List[str]:
        return [rel.owner.data_source_user.username for rel in getattr(obj, "_prefetched_owner_relations", [])]


def _validate_duplicate_data_source_username(data_source_id: str, username: str, data_source_user_id: int = 0) -> str:
    """校验数据源用户名是否重复"""
    queryset = DataSourceUser.objects.filter(data_source_id=data_source_id, username=username)
    # 过滤掉自身
    if data_source_user_id:
        queryset = queryset.exclude(id=data_source_user_id)

    if queryset.exists():
        raise ValidationError(_("用户名 {} 已存在").format(username))

    return username


class VirtualUserCreateInputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="用户名", validators=[validate_data_source_user_username])
    full_name = serializers.CharField(help_text="姓名")
    app_codes = serializers.ListField(help_text="应用编码列表", child=serializers.CharField())
    owners = serializers.ListField(help_text="责任人列表", child=serializers.CharField())
    email = serializers.EmailField(help_text="邮箱", required=False, default="", allow_blank=True)
    phone = serializers.CharField(help_text="手机号", required=False, default="", allow_blank=True)
    phone_country_code = serializers.CharField(
        help_text="手机国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE, allow_blank=True
    )

    def validate_username(self, username: str) -> str:
        return _validate_duplicate_data_source_username(self.context["data_source_id"], username)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # 如果提供了手机号，则校验手机号是否合法
        if attrs["phone"]:
            try:
                validate_phone_with_country_code(phone=attrs["phone"], country_code=attrs["phone_country_code"])
            except ValueError as e:
                raise ValidationError(str(e))

        return attrs

    def validate_app_codes(self, app_codes: list[str]) -> list[str]:
        # 过滤重复值
        return list(set(app_codes))

    def validate_owners(self, owners: list[str]) -> list[str]:
        # 过滤重复值
        owners = list(set(owners))
        # 责任人必须存在且为实体用户
        for owner in owners:
            if not TenantUser.objects.filter(
                data_source_user__username=owner,
                data_source__type=DataSourceTypeEnum.REAL,
            ).exists():
                raise ValidationError(_("用户 {} 不存在或不是实体用户").format(owner))

        return owners


class VirtualUserCreateOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")


class VirtualUserRetrieveOutputSLZ(VirtualUserListOutputSLZ):
    pass


class VirtualUserUpdateInputSLZ(serializers.Serializer):
    full_name = serializers.CharField(help_text="姓名")
    app_codes = serializers.ListField(help_text="应用编码列表", child=serializers.CharField())
    owners = serializers.ListField(help_text="责任人列表", child=serializers.CharField())
    email = serializers.EmailField(help_text="邮箱", required=False, default="", allow_blank=True)
    phone = serializers.CharField(help_text="手机号", required=False, default="", allow_blank=True)
    phone_country_code = serializers.CharField(
        help_text="手机国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE, allow_blank=True
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # 如果提供了手机号，则校验手机号是否合法
        if attrs["phone"]:
            try:
                validate_phone_with_country_code(phone=attrs["phone"], country_code=attrs["phone_country_code"])
            except ValueError as e:
                raise ValidationError(str(e))

        return attrs

    def validate_app_codes(self, app_codes: list[str]) -> list[str]:
        # 过滤重复值
        return list(set(app_codes))

    def validate_owners(self, owners: list[str]) -> list[str]:
        # 过滤重复值
        owners = list(set(owners))
        # 责任人必须存在且为实体用户
        for owner in owners:
            if not TenantUser.objects.filter(
                data_source_user__username=owner,
                data_source__type=DataSourceTypeEnum.REAL,
            ).exists():
                raise ValidationError(_("用户 {} 不存在或不是实体用户").format(owner))

        return owners
