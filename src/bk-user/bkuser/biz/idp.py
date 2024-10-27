# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
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
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
import operator
from functools import reduce
from typing import Any, Dict, List

from django.db.models import Q

from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.idp.data_models import DataSourceMatchRule
from bkuser.apps.idp.models import Idp
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import TenantUserCustomField, UserBuiltinField


class AuthenticationMatcher:
    """认证匹配，用于对认证后的用户字段匹配到对应的数据源"""

    def __init__(self, idp_id: str):
        self.idp = Idp.objects.get(id=idp_id)
        # 内置字段
        self.builtin_field_data_type_map = dict(UserBuiltinField.objects.all().values_list("name", "data_type"))
        # Note: Local登录允许匹配ID
        self.builtin_field_data_type_map["id"] = UserFieldDataType.NUMBER
        # 自定义字段
        self.custom_field_data_type_map = dict(
            TenantUserCustomField.objects.filter(tenant_id=self.idp.owner_tenant_id).values_list("name", "data_type")
        )

    def match(self, idp_users: List[Dict[str, Any]]) -> List[int]:
        """匹配出数据源用户ID"""
        # 将规则转换为Django Queryset 过滤条件, 不同用户之间过滤逻辑是OR
        conditions = [
            condition for userinfo in idp_users if (condition := self._convert_rules_to_queryset_filter(userinfo))
        ]

        if not conditions:
            return []
        # 查询数据源用户
        return DataSourceUser.objects.filter(reduce(operator.or_, conditions)).values_list("id", flat=True)

    def _convert_rules_to_queryset_filter(self, source_data: Dict[str, Any]) -> Q | None:
        """
        将规则列表转换为Queryset查询条件
        不同匹配规则之间的关系是OR, 匹配规则里不同字段的关系是AND
        """
        q_list = [
            q
            for rule in self.idp.data_source_match_rule_objs
            if (q := self._convert_one_rule_to_queryset_filter(rule, source_data))
        ]
        return reduce(operator.or_, q_list) if q_list else None

    def _convert_one_rule_to_queryset_filter(
        self, match_rule: DataSourceMatchRule, source_data: Dict[str, Any]
    ) -> Q | None:
        """
        将匹配规则转换为Django QuerySet过滤条件
        :param match_rule: 匹配规则
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
        conditions = [{"data_source_id": match_rule.data_source_id}]
        # 无字段比较，相当于无法匹配，直接返回
        if not match_rule.field_compare_rules:
            return None

        # 每个认证源字段与数据源字段的比较规则
        for rule in match_rule.field_compare_rules:
            # 数据里没有规则需要比较的字段，则一定无法匹配，无需继续
            if rule.source_field not in source_data:
                return None

            filter_key = self._build_field_filter_key(rule.target_field)
            if not filter_key:
                return None

            # Note: 目前仅仅是equal的比较操作符，所以这里暂时简单处理，
            #  后续支持其他操作符再抽象出Converter来处理
            conditions.append({filter_key: source_data[rule.source_field]})

        return reduce(operator.and_, [Q(**c) for c in conditions])

    def _build_field_filter_key(self, field: str) -> str | None:
        """
        构建字段的Django过滤Key
        1. 内建字段，key=field
        2. 用户自定义字段，在extras字段里，以JSON方式存储
          - data_type=string/number/enum: key=f"extras__{field}"
          - data_type=multi_enum: key=f"extras__{field}__contains"

        Django JSONField查询: https://docs.djangoproject.com/en/3.2/topics/db/queries/#querying-jsonfield
        Note: JSON查询性能出现问题时，可以通过额外运维方式创建虚列索引来解决
          ALTER TABLE my_table ADD COLUMN field_col INT AS (JSON_UNQUOTE(JSON_EXTRACT(extras, '$.my_field'))) VIRTUAL;
          CREATE INDEX idx_field_col ON my_table (field_col); 最好与data_source_id字段一起联合索引
        """
        # 内建字段
        if field in self.builtin_field_data_type_map:
            return field

        # 自定义字段，且data_type=string/number/enum
        if field in self.custom_field_data_type_map:
            data_type = self.custom_field_data_type_map[field]
            # string/number/enum
            if data_type in [UserFieldDataType.STRING, UserFieldDataType.NUMBER, UserFieldDataType.ENUM]:
                return f"extras__{field}"

            # multi_enum
            if data_type in UserFieldDataType.MULTI_ENUM:
                return f"extras__{field}__contains"

        # 非预期的字段和数据类型，都无法匹配
        return None
