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
from rest_framework import serializers

from bkuser_core.departments.models import Department


class DepartmentCreatedReturnSerializer(serializers.ModelSerializer):
    has_children = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        ref_name = "v2_department"
        model = Department
        fields = ("id", "name", "order", "enabled", "full_name", "has_children", "category_id")

    def get_full_name(self, obj):
        return obj.full_name

    def get_has_children(self, obj) -> bool:
        """仅返回启用的子部门"""
        # Q: 为什么不用 obj.children.filter(enabled=True).exists()?
        # A: 因为 get_descendants 是访问 tree_id 这类的 int 字段，而 children 访问的是 parent 外键字段，前者明显更快
        return obj.get_descendants(include_self=False).filter(enabled=True).exists()


class DepartmentCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    parent = serializers.IntegerField(required=False)
    category_id = serializers.IntegerField()


class DepartmentSearchSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()


class DepartmentSearchResultSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    category_id = serializers.IntegerField(required=False)
