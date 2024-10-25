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

from rest_framework import serializers

from bkuser.common.serializers import StringArrayField


class ProfileFieldsSLZ(serializers.Serializer):
    """用户字段校验"""

    fields = StringArrayField(help_text="指定返回的用户字段", required=False)

    def validated_fields(self, fields: List[str]) -> List[str]:
        # 不再支持返回的字段：
        #  [基本] code, qq
        #  [登录&密码相关] password_valid_days, password_update_time, last_login_time, account_expiration_date,
        #  [时间相关] create_time, update_time
        # 总返回固定值字段：logo, type, role
        allowed_fields = {
            # 基础字段
            "id",
            "username",
            "display_name",  # 目前返回值是姓名，即 full_name，后续根据表达式展示
            "email",
            "telephone",
            "country_code",
            "iso_code",
            "time_zone",
            "language",
            "extras",
            # 微信消息通知相关
            "wx_userid",
            "wx_openid",
            # 原目录相关
            "domain",
            "category_id",
            # 生命周期相关
            "status",
            "staff_status",
            "enabled",
            # 关联关系
            "departments",
            "leader",
        }

        # 忽略无效的指定字段
        return list(set(fields) & allowed_fields)


class ProfileRetrieveInputSLZ(ProfileFieldsSLZ):
    lookup_field = serializers.ChoiceField(
        help_text="指定路径参数值的字段", choices=["id", "username"], required=False, default="username"
    )


class ProfileListInputSLZ(ProfileFieldsSLZ):
    lookup_field = serializers.ChoiceField(
        help_text="字段名称",
        choices=[
            "id",
            "username",
            "display_name",
            "email",
            "telephone",
            # 微信消息通知相关
            "wx_userid",
            # 原目录相关
            "domain",
            "category_id",
            # 生命周期相关
            "status",
            "staff_status",
            # IAM 特有
            "create_time",
        ],
        required=False,
        default="username",
    )
    exact_lookups = StringArrayField(help_text="精确匹配字段", required=False)
    fuzzy_lookups = StringArrayField(help_text="模糊匹配字段", required=False)
    no_page = serializers.BooleanField(help_text="全量返回", required=False, default=False)


class DepartmentProfileListInputSLZ(serializers.Serializer):
    recursive = serializers.BooleanField(help_text="是否递归", required=False, default=False)
    no_page = serializers.BooleanField(help_text="全量返回", required=False, default=False)


class ProfileLanguageUpdateInputSLZ(serializers.Serializer):
    language = serializers.ChoiceField(help_text="需设置的语言", choices=["zh-cn", "en"])
