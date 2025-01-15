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
from rest_framework import serializers

from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.tenant import TenantUserHandler
from bkuser.common.serializers import StringArrayField


class TenantUserContactInfoListInputSLZ(serializers.Serializer):
    bk_usernames = StringArrayField(
        help_text="蓝鲸用户唯一标识，多个使用逗号分隔",
        max_items=100,
    )


class TenantUserContactInfoListOutputSLZ(serializers.Serializer):
    bk_username = serializers.CharField(help_text="蓝鲸用户唯一标识", source="id")
    tenant_id = serializers.CharField(help_text="租户 ID")
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")
    phone = serializers.SerializerMethodField(help_text="手机号")
    phone_country_code = serializers.SerializerMethodField(help_text="手机国际区号")
    email = serializers.CharField(help_text="邮箱")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)

    def get_phone(self, obj: TenantUser) -> str:
        return obj.phone_info[0]

    def get_phone_country_code(self, obj: TenantUser) -> str:
        return obj.phone_info[1]
