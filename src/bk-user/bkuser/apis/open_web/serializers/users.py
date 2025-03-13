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

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.tenant import TenantUserHandler
from bkuser.common.serializers import StringArrayField


class TenantUserDisplayInfoRetrieveOutputSLZ(serializers.Serializer):
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
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)


class TenantUserSearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", min_length=2, max_length=64)
    data_source_type = serializers.ChoiceField(
        help_text="数据源类型",
        choices=[DataSourceTypeEnum.REAL, DataSourceTypeEnum.VIRTUAL],
        required=False,
        allow_blank=True,
        default="",
    )
    owner_tenant_id = serializers.CharField(help_text="归属租户 ID", required=False, allow_blank=True, default="")


class TenantUserSearchOutputSLZ(serializers.Serializer):
    bk_username = serializers.CharField(help_text="蓝鲸用户唯一标识", source="id")
    # 用 login_name 对外暴露 username 字段，作为企业内用户唯一标识
    login_name = serializers.CharField(help_text="企业内用户唯一标识", source="data_source_user.username")
    full_name = serializers.CharField(help_text="用户姓名", source="data_source_user.full_name")
    # TODO: 虚拟帐号先暂时使用 display_name 展示，后续根据虚拟帐号方案再进行更改
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")
    data_source_type = serializers.CharField(help_text="数据源用户类型", source="data_source.type")
    owner_tenant_id = serializers.CharField(help_text="归属租户 ID", source="data_source.owner_tenant_id")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)


class TenantUserListInputSLZ(serializers.Serializer):
    lookups = StringArrayField(help_text="精确匹配值，多个使用逗号分隔", max_items=100)
    lookup_fields = StringArrayField(
        help_text="匹配字段，多个使用逗号分隔",
        required=False,
        default=["login_name"],
    )
    data_source_type = serializers.ChoiceField(
        help_text="数据源类型", choices=DataSourceTypeEnum.get_choices(), required=False, allow_blank=True, default=""
    )
    owner_tenant_id = serializers.CharField(help_text="归属租户 ID", required=False, allow_blank=True, default="")


class TenantUserListOutputSLZ(serializers.Serializer):
    bk_username = serializers.CharField(help_text="蓝鲸用户唯一标识", source="id")
    login_name = serializers.CharField(help_text="企业内用户唯一标识", source="data_source_user.username")
    full_name = serializers.CharField(help_text="用户姓名", source="data_source_user.full_name")
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")
    data_source_type = serializers.CharField(help_text="用户类型", source="data_source.type")
    owner_tenant_id = serializers.CharField(help_text="归属租户 ID", source="data_source.owner_tenant_id")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)
