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
from typing import List

from pydantic import BaseModel, TypeAdapter

from .constants import AllowBindScopeObjectType


class DataSourceMatchRule(BaseModel):
    """认证源与数据源匹配规则"""

    # 认证源原始字段
    source_field: str
    # 匹配的数据源 ID
    data_source_id: int
    # 匹配的数据源字段
    target_field: str


DataSourceMatchRuleList = TypeAdapter(List[DataSourceMatchRule])


class AllowBindScope(BaseModel):
    """允许关联社会化认证源的租户组织架构范围"""

    # 范围对象的类型
    type: AllowBindScopeObjectType
    # 范围对象的ID
    id: str
