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

# from bkuser_core.api.web.department.serializers import DepartmentSerializer
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.departments.models import Department


class CategoryOutputSLZ(serializers.ModelSerializer):
    class Meta:
        model = ProfileCategory
        fields = "__all__"


class DepartmentListResultDepartmentOutputSLZ(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    # order = serializers.IntegerField(required=False)
    order = serializers.IntegerField(read_only=True)
    # extras = serializers.JSONField(required=False)
    enabled = serializers.BooleanField(default=True, read_only=True)

    category_id = serializers.IntegerField(read_only=True)

    # full_name = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField(read_only=True)

    # def get_full_name(self, obj):
    #     return obj.full_name

    def get_has_children(self, obj) -> bool:
        return obj.has_children

    class Meta:
        model = Department
        # fields = ("id", "name", "order", "extras", "enabled", "full_name", "has_children", "category_id")
        fields = ("id", "name", "enabled", "has_children", "category_id", "order")
        # fields = ("id", "name", "enabled", "has_children")
        # exclude = ("profiles", "update_time", "create_time", "lft", "rght", "tree_id", "level", "parent", "code")


class DepartmentListResultCategoryOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    order = serializers.IntegerField(read_only=True)
    default = serializers.BooleanField(read_only=True)

    type = serializers.CharField(read_only=True)

    profile_count = serializers.IntegerField(read_only=True)
    departments = DepartmentListResultDepartmentOutputSLZ(read_only=True, many=True)
