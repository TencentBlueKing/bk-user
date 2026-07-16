# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
from rest_framework import fields, serializers


class PasswordRuleSerializer(serializers.Serializer):
    """密码规则序列化器"""

    # --- 长度限制类 ---
    min_length = fields.IntegerField(help_text="密码最小长度")
    max_length = fields.IntegerField(help_text="密码最大长度")
    # --- 字符限制类 ---
    contain_lowercase = fields.BooleanField(help_text="必须包含小写字母")
    contain_uppercase = fields.BooleanField(help_text="必须包含大写字母")
    contain_digit = fields.BooleanField(help_text="必须包含数字")
    contain_punctuation = fields.BooleanField(help_text="必须包含特殊字符（标点符号）")
    # --- 连续性限制类 ---
    not_continuous_count = fields.IntegerField(help_text="密码不允许连续 N 位出现")
    not_keyboard_order = fields.BooleanField(help_text="不允许键盘序")
    not_continuous_letter = fields.BooleanField(help_text="不允许连续字母序")
    not_continuous_digit = fields.BooleanField(help_text="不允许连续数字序")
    not_repeated_symbol = fields.BooleanField(help_text="重复字母，数字，特殊字符")
    # --- 规则提示 ---
    rule_tips = fields.ListField(help_text="用户密码规则提示", child=fields.CharField(), source="tips")
