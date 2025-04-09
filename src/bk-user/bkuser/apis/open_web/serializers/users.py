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

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.tenant import TenantUserHandler
from bkuser.common.constants import BkLanguageEnum
from bkuser.common.serializers import StringArrayField


class TenantUserDisplayInfoRetrieveOutputSLZ(serializers.Serializer):
    login_name = serializers.CharField(help_text="企业内用户唯一标识", source="data_source_user.username")
    full_name = serializers.CharField(help_text="用户姓名", source="data_source_user.full_name")
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)


class TenantUserDisplayInfoListInputSLZ(serializers.Serializer):
    bk_usernames = StringArrayField(
        help_text="蓝鲸用户唯一标识，多个使用逗号分隔",
        max_items=settings.BATCH_QUERY_USER_DISPLAY_INFO_BY_BK_USERNAME_LIMIT,
    )


class TenantUserDisplayInfoListOutputSLZ(serializers.Serializer):
    bk_username = serializers.CharField(help_text="蓝鲸用户唯一标识", source="id")
    login_name = serializers.CharField(help_text="企业内用户唯一标识", source="data_source_user.username")
    full_name = serializers.CharField(help_text="用户姓名", source="data_source_user.full_name")
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)


class TenantUserSearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", min_length=1, max_length=64)
    data_source_type = serializers.ChoiceField(
        help_text="数据源类型",
        choices=[DataSourceTypeEnum.REAL, DataSourceTypeEnum.VIRTUAL],
        required=False,
        allow_blank=True,
        default="",
    )
    owner_tenant_id = serializers.CharField(help_text="归属租户 ID", required=False, allow_blank=True, default="")
    with_organization_paths = serializers.BooleanField(
        help_text="是否返回用户所属部门路径", required=False, default=False
    )


class TenantUserSearchOutputSLZ(serializers.Serializer):
    bk_username = serializers.CharField(help_text="蓝鲸用户唯一标识", source="id")
    # 用 login_name 对外暴露 username 字段，作为企业内用户唯一标识
    login_name = serializers.CharField(help_text="企业内用户唯一标识", source="data_source_user.username")
    full_name = serializers.CharField(help_text="用户姓名", source="data_source_user.full_name")
    # TODO: 虚拟帐号先暂时使用 display_name 展示，后续根据虚拟帐号方案再进行更改
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")
    data_source_type = serializers.CharField(help_text="数据源用户类型", source="data_source.type")
    owner_tenant_id = serializers.CharField(help_text="归属租户 ID", source="data_source.owner_tenant_id")
    organization_paths = serializers.SerializerMethodField(help_text="用户所属部门路径")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)

    def get_organization_paths(self, obj: TenantUser) -> List[str]:
        return self.context["org_path_map"].get(obj.data_source_user_id, [])

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not self.context["with_organization_paths"]:
            data.pop("organization_paths")
        return data


class TenantUserLookupInputSLZ(serializers.Serializer):
    lookups = StringArrayField(help_text="精确匹配值，多个使用逗号分隔", max_items=100)
    lookup_fields = StringArrayField(help_text="匹配字段，多个使用逗号分隔")
    data_source_type = serializers.ChoiceField(
        help_text="数据源类型",
        choices=[DataSourceTypeEnum.REAL, DataSourceTypeEnum.VIRTUAL],
        required=False,
        allow_blank=True,
        default="",
    )
    owner_tenant_id = serializers.CharField(help_text="归属租户 ID", required=False, allow_blank=True, default="")
    with_organization_paths = serializers.BooleanField(
        help_text="是否返回用户所属部门路径", required=False, default=False
    )

    def validate_lookups(self, lookups: List[str]) -> List[str]:
        max_length = 64
        if invalid_lookups := [i for i in lookups if len(i) > max_length]:
            raise ValidationError(_("指定查询的值 {} 长度超过 64 个字符限制").format(", ".join(invalid_lookups)))
        return lookups

    def validate_lookup_fields(self, lookup_fields: List[str]) -> List[str]:
        if invalid_fields := set(lookup_fields) - {"login_name", "full_name", "bk_username"}:
            raise ValidationError(
                _("指定查询字段 {} 不支持，仅支持 login_name、full_name、bk_username").format(
                    ", ".join(invalid_fields)
                )
            )
        return lookup_fields


class TenantUserLookupOutputSLZ(serializers.Serializer):
    bk_username = serializers.CharField(help_text="蓝鲸用户唯一标识", source="id")
    login_name = serializers.CharField(help_text="企业内用户唯一标识", source="data_source_user.username")
    full_name = serializers.CharField(help_text="用户姓名", source="data_source_user.full_name")
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")
    data_source_type = serializers.CharField(help_text="用户类型", source="data_source.type")
    owner_tenant_id = serializers.CharField(help_text="归属租户 ID", source="data_source.owner_tenant_id")
    organization_paths = serializers.SerializerMethodField(help_text="用户所属部门路径")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)

    def get_organization_paths(self, obj: TenantUser) -> List[str]:
        return self.context["org_path_map"].get(obj.data_source_user_id, [])

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not self.context["with_organization_paths"]:
            data.pop("organization_paths")
        return data


class VirtualUserListOutputSLZ(serializers.Serializer):
    bk_username = serializers.CharField(help_text="蓝鲸用户唯一标识", source="id")
    login_name = serializers.CharField(help_text="企业内用户唯一标识", source="data_source_user.username")
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)


class CurrentUserLanguageUpdateInputSLZ(serializers.Serializer):
    language = serializers.ChoiceField(help_text="语言类型", choices=BkLanguageEnum.get_choices())
