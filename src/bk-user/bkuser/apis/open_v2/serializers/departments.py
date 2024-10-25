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

from typing import Any, Dict, List

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.common.serializers import StringArrayField


class DepartmentFieldsSLZ(serializers.Serializer):
    """部门字段校验序列化器"""

    fields = StringArrayField(help_text="需要返回的部门字段", required=False)

    def validate_fields(self, fields: List[str]) -> List[str]:
        # 不再支持提供 code、lft、rght、tree_id 等字段，并且丢弃用户指定的无效字段
        allowed_fields = {"id", "name", "extras", "category_id", "parent", "enabled", "level", "order"}
        return list(set(fields) & allowed_fields)


class DepartmentListInputSLZ(DepartmentFieldsSLZ):
    lookup_field = serializers.ChoiceField(
        help_text="字段名称",
        choices=["id", "name", "category_id", "parent", "level"],
        required=False,
    )
    exact_lookups = StringArrayField(help_text="精确匹配字段", required=False)
    fuzzy_lookups = StringArrayField(help_text="模糊匹配字段", required=False)
    with_ancestors = serializers.BooleanField(help_text="是否返回上级部门", default=False)
    no_page = serializers.BooleanField(help_text="全量返回", default=False)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        lookup_field = attrs.get("lookup_field")
        exact_lookups = attrs.get("exact_lookups")
        fuzzy_lookups = attrs.get("fuzzy_lookups")

        if lookup_field:
            if not (exact_lookups or fuzzy_lookups):
                raise ValidationError("exact_lookups or fuzzy_lookups required")

            # 其他字段都是整型，无需模糊匹配
            if lookup_field != "name" and fuzzy_lookups:
                raise ValidationError("fuzzy_lookups only supported when lookup_field is name")

        return attrs


class DepartmentRetrieveInputSLZ(DepartmentFieldsSLZ):
    with_ancestors = serializers.BooleanField(help_text="是否返回上级部门", default=False)


class ProfileDepartmentListInputSLZ(serializers.Serializer):
    lookup_field = serializers.ChoiceField(help_text="字段名称", choices=["id", "username"], default="username")
    with_ancestors = serializers.BooleanField(help_text="是否返回上级部门", default=False)
    with_family = serializers.BooleanField(help_text="兼容参数（与 with_ancestors 等价）", default=False)
