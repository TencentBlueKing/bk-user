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
from typing import Dict, List

from rest_framework import serializers

from bkuser_core.departments.models import Department


class RapidDepartmentSerializer(serializers.Serializer):
    """极简返回"""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class DepartmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    order = serializers.IntegerField(required=False)
    extras = serializers.JSONField(required=False)
    enabled = serializers.BooleanField(default=True, required=False)

    full_name = serializers.CharField()
    has_children = serializers.BooleanField()

    class Meta:
        model = Department
        exclude = ("profiles", "update_time", "create_time", "lft", "rght", "tree_id", "level", "parent", "code")


class DepartmentWithChildrenSLZ(DepartmentSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj) -> List[Dict]:
        """不使用 serializer 而是手动取数据，避免重复查询 DB"""
        full_name_prefix = obj.full_name

        data = []
        items = set()
        all_children = obj.children.filter(enabled=True)
        for x in all_children:
            # children 可能存在重复
            if x.pk in items:
                continue
            items.add(x.pk)

            full_name = f"{full_name_prefix}/{x.name}"
            # 由于当前删除是假删除，真实架构树并未移除 has_children = not x.is_leaf_node()
            has_children = x.get_children().filter(enabled=True).exists()
            y = {"id": x.pk, "name": x.name, "full_name": full_name, "has_children": has_children, "order": x.order}
            data.append(y)

        # sort by order asc
        data.sort(key=lambda x: x["order"])
        return data


class DepartmentsWithChildrenAndAncestorsOutputSLZ(DepartmentWithChildrenSLZ):
    ancestors = serializers.SerializerMethodField()

    # 用户点击某一个部门, 调用接口拉取数据并展开, 此时这个接口只返回当前部门的 `profile_count`
    # `children`和`ancestors`里面没有`profile_count`
    profile_count = serializers.SerializerMethodField()

    def get_ancestors(self, instance) -> List:
        family = instance.get_ancestors()
        return RapidDepartmentSerializer(family, many=True).data

    def get_profile_count(self, instance) -> int:
        return instance.get_profile_count(recursive=True)


class DepartmentCreatedOutputSLZ(DepartmentSerializer):
    class Meta:
        # ref_name = "v2_department"
        model = Department
        fields = ("id", "name", "order", "enabled", "full_name", "has_children", "category_id")


class DepartmentCreateInputSLZ(serializers.Serializer):
    name = serializers.CharField()
    parent = serializers.IntegerField(required=False)
    category_id = serializers.IntegerField()


class DepartmentSearchInputSLZ(serializers.Serializer):
    category_id = serializers.IntegerField(required=True)


class DepartmentSearchOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    category_id = serializers.IntegerField(required=False)


class DepartmentProfileListInputSLZ(serializers.Serializer):
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=10)
    recursive = serializers.BooleanField(default=True)
    keyword = serializers.CharField(required=False)


class DepartmentProfilesCreateInputSLZ(serializers.Serializer):
    profile_id_list = serializers.ListField(child=serializers.IntegerField())
