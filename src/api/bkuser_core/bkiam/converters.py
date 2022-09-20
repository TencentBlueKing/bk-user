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

from django.db.models import Q
from iam import OP
from iam.contrib.converter.queryset import DjangoQuerySetConverter


def mark_non_leaf_policies(content: list) -> list:
    # 为什么要标记非叶子节点？
    # 因为对于包含路径的策略，权限中心针对中间节点和叶子节点有不同的存储方式
    # 对于叶子节点：
    # [
    #   {'field': 'department.id', 'op': 'eq', 'value': '3469'},
    #   {'field': 'department._bk_iam_path_', 'op': 'starts_with',
    #    'value': '/category,1/department,3351/department,3352/department,3353/department,3449/'}], 'op': 'AND'}
    # ]
    # 返回的策略中会包含 id: target_id
    # 对于中间节点：
    # {'field': 'department._bk_iam_path_', 'op': 'starts_with', 'value': '/category,1/department,1/department,3450/'}
    # 会将 target_id 放到路径中的最后一个

    for c in content:
        # 意味着还有更多条件，即叶子节点
        if "content" in c:
            continue

        if c["field"].endswith("._bk_iam_path_"):
            # 标记该节点为中间节点
            c["node_type"] = "non-leaf"

    return content


def mark_complex_policies(content: list) -> list:
    # 当条件本身是通过 AND 组装的，说明了 content 内的所有条件指向了同一条权限
    # 此时 _bk_iam_path_ 表示的是目标对象的父对象， 所以这里我们需要为这条数据标记
    # [
    #   {'field': 'department.id', 'op': 'eq', 'value': '3469'},
    #   {'field': 'department._bk_iam_path_', 'op': 'starts_with',
    #    'value': '/category,1/department,3351/department,3352/department,3353/department,3449/'}], 'op': 'AND'}
    # ]
    for c in content:
        if c["field"].endswith("._bk_iam_path_"):
            # 标记该节点为父节点（将跳过中间节点标记）
            c["node_type"] = "parent-node"

    return content


class PathIgnoreDjangoQSConverter(DjangoQuerySetConverter):
    """DjangoQS Converter 特性：忽略 path filter"""

    def operator_map(self, operator, field, value):
        if field.endswith("._bk_iam_path_") and operator == OP.STARTS_WITH:
            return self._eq

    def _and(self, content):
        return reduce(
            operator.and_,
            [self.convert(c) for c in mark_complex_policies(content) if self.convert(c)],
        )

    def _or(self, content):
        return reduce(
            operator.or_,
            [self.convert(c) for c in mark_non_leaf_policies(content) if self.convert(c)],
        )

    def _any(self, left, right):
        # https://stackoverflow.com/questions/33517468/always-true-q-object
        # ~Q(pk__in=[]) => not in? should check the sql/performance

        # NOTE: We think the pk is not null in mysql schema here
        # => will genreate `pk not null`` in sql, will cause performance issue
        # return ~Q(pk=None)

        # => will generate where condition in sql
        return ~Q(pk__in=[])

    def convert(self, data):
        op = data["op"]

        if op == OP.AND:
            return self._and(data["content"])
        elif op == OP.OR:
            return self._or(data["content"])
        elif op == OP.STARTS_WITH:
            # 当该条策略（递归后）未被 AND 条件标记为父节点，则标记为中间节点
            if not data.get("node_type") == "parent-node":
                data["node_type"] = "non-leaf"

        value = data["value"]
        field = data["field"]

        op_func = self.operator_map(op, field, value)

        if not op_func:
            op_func = {
                OP.EQ: self._eq,
                OP.NOT_EQ: self._not_eq,
                OP.IN: self._in,
                OP.NOT_IN: self._not_in,
                OP.CONTAINS: self._contains,
                OP.NOT_CONTAINS: self._not_contains,
                OP.STARTS_WITH: self._starts_with,
                OP.NOT_STARTS_WITH: self._not_starts_with,
                OP.ENDS_WITH: self._ends_with,
                OP.NOT_ENDS_WITH: self._not_ends_with,
                OP.LT: self._lt,
                OP.LTE: self._lte,
                OP.GT: self._gt,
                OP.GTE: self._gte,
                OP.ANY: self._any,
            }.get(op)

        if op_func is None:
            raise ValueError("invalid op %s" % op)

        if self.key_mapping and field in self.key_mapping:
            # 隐含的条件，当 key_mapping 为空时，不作为转换条件
            _f = self.key_mapping.get(field)
            if not _f:
                return None

            if isinstance(_f, str):
                field = _f
            elif callable(_f):
                field, value = _f(data)
            else:
                field = _f

        if (field in self.value_hooks) and callable(self.value_hooks[field]):
            value = self.value_hooks[field](value)

        return op_func(field, value)
