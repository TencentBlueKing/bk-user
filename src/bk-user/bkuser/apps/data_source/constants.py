# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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
from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _

from bkuser.plugins.local.constants import USERNAME_REGEX as DATA_SOURCE_USERNAME_REGEX  # noqa: F401

# 批量更新数据源用户自定义字段单次操作数量
USER_EXTRAS_UPDATE_BATCH_SIZE = 250


class FieldMappingOperation(str, StructuredEnum):
    """字段映射关系"""

    DIRECT = EnumField("direct", label=_("直接"))
    EXPRESSION = EnumField("expression", label=_("表达式"))


class DataSourceTypeEnum(str, StructuredEnum):
    """数据源类型"""

    REAL = EnumField("real", label=_("实体"))
    VIRTUAL = EnumField("virtual", label=_("虚拟"))
    BUILTIN_MANAGEMENT = EnumField("builtin_management", label=_("内置管理"))
