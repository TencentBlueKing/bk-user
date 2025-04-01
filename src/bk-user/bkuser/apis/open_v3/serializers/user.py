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
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ChoiceField

from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.tenant import TenantUserHandler
from bkuser.common.constants import TIME_ZONE_CHOICES, BkLanguageEnum
from bkuser.common.serializers import StringArrayField


class TenantUserDisplayInfoListInputSLZ(serializers.Serializer):
    bk_usernames = StringArrayField(
        help_text="蓝鲸用户唯一标识，多个使用逗号分隔",
        max_items=settings.BATCH_QUERY_USER_DISPLAY_INFO_BY_BK_USERNAME_LIMIT,
    )


class TenantUserDisplayInfoListOutputSLZ(serializers.Serializer):
    bk_username = serializers.CharField(help_text="蓝鲸用户唯一标识", source="id")
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)


class TenantUserRetrieveOutputSLZ(serializers.Serializer):
    tenant_id = serializers.CharField(help_text="租户 ID")
    bk_username = serializers.CharField(help_text="蓝鲸用户唯一标识", source="id")
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")
    time_zone = serializers.ChoiceField(help_text="时区", choices=TIME_ZONE_CHOICES)
    language = serializers.ChoiceField(help_text="语言", choices=BkLanguageEnum.get_choices())

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)


class AncestorSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="祖先部门 ID")
    name = serializers.CharField(help_text="祖先部门名称")

    class Meta:
        ref_name = "open_v3.user.AncestorSLZ"


class TenantUserDepartmentListInputSLZ(serializers.Serializer):
    with_ancestors = serializers.BooleanField(help_text="是否包括祖先部门", required=False, default=False)


class TenantUserDepartmentListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门 ID")
    name = serializers.CharField(help_text="部门名称")
    ancestors = serializers.ListField(help_text="祖先部门列表", required=False, child=AncestorSLZ(), allow_empty=True)


class TenantUserLeaderListOutputSLZ(serializers.Serializer):
    bk_username = serializers.CharField(help_text="蓝鲸用户唯一标识", source="id")
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)


class TenantUserListOutputSLZ(serializers.Serializer):
    bk_username = serializers.CharField(help_text="蓝鲸用户唯一标识", source="id")
    full_name = serializers.CharField(help_text="姓名", source="data_source_user.full_name")
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)


class TenantUserSensitiveInfoListInputSLZ(serializers.Serializer):
    bk_usernames = StringArrayField(help_text="蓝鲸用户唯一标识，多个使用逗号分隔", max_items=100)


class TenantUserSensitiveInfoListOutputSLZ(serializers.Serializer):
    bk_username = serializers.CharField(help_text="蓝鲸用户唯一标识", source="id")
    phone = serializers.SerializerMethodField(help_text="手机号")
    phone_country_code = serializers.SerializerMethodField(help_text="手机国际区号")
    email = serializers.CharField(help_text="邮箱")
    wx_userid = serializers.CharField(help_text="微信 ID")

    def get_phone(self, obj: TenantUser) -> str:
        return obj.phone_info[0]

    def get_phone_country_code(self, obj: TenantUser) -> str:
        return obj.phone_info[1]


class VirtualUserLookupInputSLZ(serializers.Serializer):
    lookups = StringArrayField(help_text="精确匹配值，多个使用逗号分隔", max_items=100)
    lookup_field = ChoiceField(help_text="匹配字段", choices=["login_name", "bk_username"])

    def validate_lookups(self, lookups: List[str]) -> List[str]:
        max_length = 64
        if invalid_lookups := [i for i in lookups if len(i) > max_length]:
            raise ValidationError(
                "The length of the specified lookup value {} exceeds the 64-character limit.".format(
                    ", ".join(invalid_lookups)
                )
            )
        return lookups


class VirtualUserLookupOutputSLZ(serializers.Serializer):
    bk_username = serializers.CharField(help_text="蓝鲸用户唯一标识", source="id")
    login_name = serializers.CharField(help_text="企业内用户唯一标识", source="data_source_user.username")
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)
