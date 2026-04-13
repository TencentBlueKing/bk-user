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
from typing import Optional

from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel, field_validator, model_validator

from bkuser.apps.data_source.constants import (
    USERNAME_PREFIX_REGEX,
    USERNAME_SUFFIX_REGEX,
    FieldMappingOperation,
    UsernameConflictStrategy,
)


class DataSourceUserFieldMapping(BaseModel):
    """数据源用户字段映射"""

    # 数据源原始字段
    source_field: str
    # 映射关系
    mapping_operation: FieldMappingOperation
    # 用户管理用户字段
    target_field: str
    # 表达式内容，仅映射关系为表达式时有效
    expression: Optional[str] = None

    def __str__(self):
        if self.mapping_operation == FieldMappingOperation.DIRECT:
            return f"{self.source_field} --> {self.target_field}"

        return f"{self.source_field} --{self.expression}--> {self.target_field}"


class DataSourceConflictConfig(BaseModel):
    """数据源冲突配置"""

    # 冲突处理策略，默认为手动处理
    strategy: UsernameConflictStrategy = UsernameConflictStrategy.MANUAL
    # 用户名前缀，格式：1-6 位字母或数字 + 一个分隔符("-" 或 "_")，如 "ldap_"、"http-"
    prefix: str = ""
    # 用户名后缀，格式：一个分隔符("-" 或 "_") + 1-6 位字母或数字，如 "-ldap"、"_http"
    suffix: str = ""

    @field_validator("prefix")
    @classmethod
    def validate_prefix(cls, v: str) -> str:
        if not v:
            return v
        if not USERNAME_PREFIX_REGEX.fullmatch(v):
            raise ValueError(_("{} 不符合 用户名前缀 的命名规范，应为 1-6 位大小写字母或数字").format(v))
        return v

    @field_validator("suffix")
    @classmethod
    def validate_suffix(cls, v: str) -> str:
        if not v:
            return v
        if not USERNAME_SUFFIX_REGEX.fullmatch(v):
            raise ValueError(_("{} 不符合 用户名后缀 的命名规范，应为 1-6 位大小写字母或数字").format(v))
        return v

    @model_validator(mode="after")
    def validate_prefix_and_suffix(self) -> "DataSourceConflictConfig":
        if self.strategy == UsernameConflictStrategy.ADD_AFFIX:
            if not self.prefix and not self.suffix:
                raise ValueError(_("添加前后缀策略下，前缀和后缀不能同时为空"))
            if self.prefix and self.suffix:
                raise ValueError(_("添加前后缀策略下，前缀和后缀不能同时配置"))

        elif self.strategy == UsernameConflictStrategy.MANUAL:
            if self.prefix or self.suffix:
                raise ValueError(_("手动处理策略下，不支持配置用户名前缀或后缀"))

        return self
