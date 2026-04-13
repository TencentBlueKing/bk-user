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
import re

from blue_krill.data_types.enum import EnumField, StrStructuredEnum
from django.utils.translation import gettext_lazy as _

from bkuser.plugins.local.constants import USERNAME_REGEX as DATA_SOURCE_USERNAME_REGEX  # noqa: F401

# 批量更新数据源用户自定义字段单次操作数量
USER_EXTRAS_UPDATE_BATCH_SIZE = 250

# 以 "_" 或 "-" 开头，后跟 1-6 个字母或数字
USERNAME_SUFFIX_REGEX = re.compile(r"^[-_][a-zA-Z0-9]{1,6}$")
# 以 "_" 或 "-" 结尾，前面为 1-6 个字母或数字
USERNAME_PREFIX_REGEX = re.compile(r"^[a-zA-Z0-9]{1,6}[-_]$")


class FieldMappingOperation(StrStructuredEnum):
    """字段映射关系"""

    DIRECT = EnumField("direct", label=_("直接"))
    EXPRESSION = EnumField("expression", label=_("表达式"))


class DataSourceTypeEnum(StrStructuredEnum):
    """数据源类型"""

    REAL = EnumField("real", label=_("实体"))
    VIRTUAL = EnumField("virtual", label=_("虚拟"))
    BUILTIN_MANAGEMENT = EnumField("builtin_management", label=_("内置管理"))


class UsernameConflictStrategy(StrStructuredEnum):
    """用户名冲突策略"""

    MANUAL = EnumField("manual", label=_("手动处理"))
    ADD_AFFIX = EnumField("add_affix", label=_("添加前后缀"))
    # TODO (mufen) 支持根据特定字段 (username / phone) 关联账号
    # LINK_ACCOUNT = EnumField("link_account", label=_("关联账号"))
