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
import operator
from functools import reduce
from typing import Any, Dict, List

from django.db.models import Q
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

    def convert_to_queryset_filter(self, source_data: Dict[str, Any]) -> Q | None:
        """
        将匹配规则转换为Django QuerySet过滤条件
        :param source_data: 认证源数据
        :return Django Queryset Q 查询表达式
            example:
            self:
                {
                    "data_source_id": 1,
                    "field_compare_rules": [
                        {"source_field": "user_id", "target_field": "username", "operator": "equal"},
                        {"source_field": "telephone", "target_field": "phone", "operator": "equal"},
                    ]
                }
            source_data: {"user_id": "zhangsan", "telephone": "12345678901", "company_email": "test@example.com"}
            return: (Q(data_source_id=1) & Q(username="zhangsan") & Q(phone="12345678901"))
        """
        conditions = [{"data_source_id": self.data_source_id}]
        # 无字段比较，相当于无法匹配，直接返回
        if not self.field_compare_rules:
            return None

        # 每个认证源字段与数据源字段的比较规则
        for rule in self.field_compare_rules:
            # 数据里没有规则需要比较的字段，则一定无法匹配，所以无需继续
            if rule.source_field not in source_data:
                return None

            conditions.append(
                {
                    # Note: 目前仅仅是equal的比较操作符，所以这里暂时简单处理，
                    #  后续支持其他操作符再抽象出Converter来处理
                    rule.target_field: source_data[rule.source_field],
                }
            )

        return reduce(operator.and_, [Q(**c) for c in conditions])


DataSourceMatchRuleList = TypeAdapter(List[DataSourceMatchRule])


def convert_match_rules_to_queryset_filter(
    match_rules: List[DataSourceMatchRule], source_data: Dict[str, Any]
) -> Q | None:
    """
    将规则列表转换为Queryset查询条件
    不同匹配规则之间的关系是OR, 匹配规则里不同字段的关系是AND
    """
    q_list = [q for rule in match_rules if (q := rule.convert_to_queryset_filter(source_data))]
    return reduce(operator.or_, q_list) if q_list else None


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
