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
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from bkuser.apps.tenant.constants import CollaborativeScopeType, FieldMappingOperation


class TenantUserCustomFieldOption(BaseModel):
    """用户自定义字段-options字段"""

    id: str
    value: str


class TenantUserFieldMapping(BaseModel):
    """数据源用户字段映射"""

    # 原始租户用户字段
    source_field: str
    # 映射关系
    mapping_operation: FieldMappingOperation
    # 目标租户用户字段
    target_field: str
    # 表达式内容，仅映射关系为表达式时有效
    expression: Optional[str] = None

    def __str__(self):
        if self.mapping_operation == FieldMappingOperation.DIRECT:
            return f"{self.source_field} --> {self.target_field}"

        return f"{self.source_field} --{self.expression}--> {self.target_field}"


class CollaborativeStrategySourceConfig(BaseModel):
    """
    租户协同策略配置（分享方）

    # TODO 后续如果支持指定范围，再考虑两个 scope_config 的建模，现在先用 Dict
    """

    organization_scope_type: CollaborativeScopeType
    organization_scope_config: Dict[str, Any] = Field(default_factory=dict)
    field_scope_type: CollaborativeScopeType
    field_scope_config: Dict[str, Any] = Field(default_factory=dict)


class CollaborativeStrategyTargetConfig(BaseModel):
    """租户协同策略配置（接受方）

    # TODO 后续如果支持指定范围，再考虑 organization_scope_config 的建模，现在先用 Dict
    """

    organization_scope_type: CollaborativeScopeType
    organization_scope_config: Dict[str, Any] = Field(default_factory=dict)
    # 注：仅支持用户自定义字段映射，因为协同数据的模型是一致的，内置字段不需要映射
    field_mapping: List[TenantUserFieldMapping]
