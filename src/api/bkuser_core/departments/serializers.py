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

from bkuser_core.common.serializers import (
    AdvancedListSerializer,
    AdvancedRetrieveSerialzier,
    CustomFieldsMixin,
    CustomFieldsModelSerializer,
)
from django.utils.translation import ugettext as _
from rest_framework import serializers

from .models import Department

# ===============================================================================
# Response
# ===============================================================================


class RapidDepartmentSerializer(serializers.Serializer):
    """极简返回"""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class SimpleDepartmentSerializer(CustomFieldsModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.full_name

    class Meta:
        model = Department
        fields = ("id", "name", "order", "full_name")


class DepartmentSerializer(CustomFieldsModelSerializer):
    name = serializers.CharField(required=True)
    has_children = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    order = serializers.IntegerField(required=False)
    extras = serializers.JSONField(required=False)
    enabled = serializers.BooleanField(default=True, required=False)

    def get_full_name(self, obj):
        return obj.full_name

    def get_has_children(self, obj) -> bool:
        """仅返回启用的子部门"""
        # Q: 为什么不用 obj.children.filter(enabled=True).exists()?
        # A: 因为 get_descendants 是访问 tree_id 这类的 int 字段，而 children 访问的是 parent 外键字段，前者明显更快
        return obj.get_descendants(include_self=False).filter(enabled=True).exists()

    class Meta:
        model = Department
        exclude = ("profiles", "update_time", "create_time")


class DepartmentWithChildrenSLZ(DepartmentSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj) -> List[Dict]:
        """不使用 serializer 而是手动取数据，避免重复查询 DB"""
        full_name_prefix = obj.full_name

        items = {}
        all_children = obj.children.filter(enabled=True)
        for x in all_children:
            # children 可能存在重复
            if x.pk in items:
                continue

            full_name = f"{full_name_prefix}/{x.name}"
            # 由于当前删除是假删除，真实架构树并未移除 has_children = not x.is_leaf_node()
            has_children = x.get_children().filter(enabled=True).exists()
            y = {"id": x.pk, "name": x.name, "full_name": full_name, "has_children": has_children}
            items.update({x.pk: y})

        return list(items.values())


class DepartmentSimpleSerializer(CustomFieldsMixin, serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    order = serializers.IntegerField(read_only=True)


class DepartmentsWithAncestorsSerializer(CustomFieldsMixin, DepartmentWithChildrenSLZ):
    ancestors = serializers.SerializerMethodField()

    def get_ancestors(self, instance) -> List:
        family = instance.get_ancestors()
        return RapidDepartmentSerializer(family, many=True).data


class DepartmentsWithFamilySerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    family = serializers.SerializerMethodField()

    def get_family(self, instance):
        family = instance.get_ancestors()
        return SimpleDepartmentSerializer(family, many=True).data


#########
# Edges #
#########
class DepartmentProfileEdgesSLZ(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    department_id = serializers.IntegerField(read_only=True)
    profile_id = serializers.IntegerField(read_only=True)


# ===============================================================================
# Request
# ===============================================================================


class DepartmentAddProfilesSerializer(serializers.Serializer):
    profile_id_list = serializers.ListField(child=serializers.IntegerField())


class DepartmentGetProfilesSerializer(AdvancedRetrieveSerialzier):
    recursive = serializers.BooleanField(required=False, default=False, help_text=_("是否递归"))
    detail = serializers.BooleanField(required=False, default=False, help_text=_("是否返回全部字段"))
    wildcard_search = serializers.CharField(required=False, help_text=_("模糊查找用户的 username & display_name 字段"))


class DepartmentListSerializer(AdvancedListSerializer):
    with_ancestors = serializers.BooleanField(default=False)


class DepartmentRetrieveSerializer(AdvancedRetrieveSerialzier):
    with_ancestors = serializers.BooleanField(default=False)


class BatchDepartmentsRetrieveSerializer(serializers.Serializer):
    department_ids = serializers.CharField(help_text="department id 列表，以 , 分隔")
    recursive = serializers.BooleanField(default=False)
