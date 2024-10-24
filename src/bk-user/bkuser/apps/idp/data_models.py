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
from typing import List

from pydantic import BaseModel, TypeAdapter

from .constants import AllowBindScopeObjectType


class FieldCompareRule(BaseModel):
    """
    数据源与认证源字段比较规则
    """

    # Note: 暂时只支持equal，后续可以支持not_equal等其他operator
    # 认证源原始字段
    source_field: str
    # 匹配的数据源字段
    target_field: str


class DataSourceMatchRule(BaseModel):
    """认证源与数据源匹配规则"""

    # 匹配的数据源 ID
    data_source_id: int
    # 字段匹配规则
    field_compare_rules: List[FieldCompareRule]


DataSourceMatchRuleList = TypeAdapter(List[DataSourceMatchRule])


def gen_data_source_match_rule_of_local(data_source_id: int) -> DataSourceMatchRule:
    """生成本地账密认证源的匹配规则"""
    return DataSourceMatchRule(
        data_source_id=data_source_id,
        field_compare_rules=[FieldCompareRule(source_field="id", target_field="id")],
    )


class AllowBindScope(BaseModel):
    """允许关联社会化认证源的租户组织架构范围"""

    # 范围对象的类型
    type: AllowBindScopeObjectType
    # 范围对象的ID
    id: str
