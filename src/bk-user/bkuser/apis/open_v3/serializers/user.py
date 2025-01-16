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

from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.tenant import TenantUserHandler
from bkuser.common.constants import TIME_ZONE_CHOICES, BkLanguageEnum
from bkuser.common.serializers import StringArrayField


class TenantUserDisplayNameListInputSLZ(serializers.Serializer):
    bk_usernames = StringArrayField(
        help_text="蓝鲸用户唯一标识，多个使用逗号分隔",
        max_items=settings.BATCH_QUERY_USER_DISPLAY_NAME_BY_BK_USERNAME_LIMIT,
    )


class TenantUserDisplayNameListOutputSLZ(serializers.Serializer):
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
