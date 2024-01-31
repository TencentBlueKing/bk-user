# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _

from bkuser.plugins.local.constants import USERNAME_REGEX as DATA_SOURCE_USERNAME_REGEX  # noqa: F401

# 批量更新数据源用户自定义字段单次操作数量
USER_EXTRAS_UPDATE_BATCH_SIZE = 250


class DataSourceStatus(str, StructuredEnum):
    """数据源状态"""

    ENABLED = EnumField("enabled", label=_("启用"))
    DISABLED = EnumField("disabled", label=_("未启用"))
    DELETED = EnumField("deleted", label=_("软删除"))


class FieldMappingOperation(str, StructuredEnum):
    """字段映射关系"""

    DIRECT = EnumField("direct", label=_("直接"))
    EXPRESSION = EnumField("expression", label=_("表达式"))


class TenantUserIdRuleEnum(str, StructuredEnum):
    """租户用户 ID 生成规则"""

    UUID4_HEX = EnumField("uuid4_hex", label=_("uuid4 hex"))
    USERNAME = EnumField("username", label=_("用户名"))
    USERNAME_WITH_DOMAIN = EnumField("username@domain", label=_("用户名@域名"))


class DataSourceUserStatus(str, StructuredEnum):
    """数据源用户状态"""

    ENABLED = EnumField("enabled", label=_("启用"))
    DISABLED = EnumField("disabled", label=_("禁用"))
    DELETED = EnumField("deleted", label=_("软删除"))


class DataSourceDepartmentStatus(str, StructuredEnum):
    """数据源部门状态"""

    ENABLED = EnumField("enabled", label=_("启用"))
    DELETED = EnumField("deleted", label=_("软删除"))
