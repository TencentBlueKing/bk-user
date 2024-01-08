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

from rest_framework import serializers


class DepartmentRetrieveInputSLZ(serializers.Serializer):
    fields = serializers.CharField(help_text="需要返回的字段", required=False)
    with_ancestors = serializers.BooleanField(help_text="是否返回上级部门", default=False)
    include_disabled = serializers.BooleanField(help_text="是否包含软删除部门", default=False)

    def validate_fields(self, fields: str) -> List[str]:
        dept_fields = [f.strip() for f in fields.split(",")]
        allowed_fields = {"id", "name", "extras", "category_id", "parent", "enabled", "level"}
        if invalid_fields := set(dept_fields) - allowed_fields:
            raise serializers.ValidationError(f"{invalid_fields} unsupported")

        return dept_fields


class ProfileDepartmentListInputSLZ(serializers.Serializer):
    lookup_field = serializers.ChoiceField(help_text="字段名称", choices=["id", "username"], required=False)
    include_disabled = serializers.BooleanField(help_text="是否包含软删除用户", default=False)
    with_ancestors = serializers.BooleanField(help_text="是否返回上级部门", default=False)
    with_family = serializers.BooleanField(help_text="兼容参数（与 with_ancestors 等价）", default=False)
