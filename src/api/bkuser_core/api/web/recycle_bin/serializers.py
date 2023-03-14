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

from bkuser_core.api.web.utils import get_category_display_name_map
from bkuser_core.recycle_bin.models import RecycleBin


class RecycleBinSearchInputSlZ(serializers.Serializer):
    keyword = serializers.CharField(required=False)


class RecycleBinBaseSerializer(serializers.ModelSerializer):
    expires = serializers.IntegerField()

    class Meta:
        model = RecycleBin
        exclude = ["create_time", "update_time", "object_type", "object_id", "status"]


class RecycleBinCategoryOutputSlZ(RecycleBinBaseSerializer):
    category = serializers.SerializerMethodField()
    profile_count = serializers.IntegerField()
    department_count = serializers.IntegerField()

    def get_category(self, instance):
        category = instance.get_map_object()
        return {
            "id": category.id,
            "display_name": category.display_name,
            "domain": category.domain,
            "type": category.type,
        }


class RecycleBinDepartmentOutputSlZ(RecycleBinBaseSerializer):
    category_display_name = serializers.SerializerMethodField()
    profile_count = serializers.IntegerField()
    department = serializers.SerializerMethodField()

    def get_department(self, instance):
        department = instance.get_map_object()
        return {
            "id": department.id,
            "name": department.name,
            "ancestor": department.parent.name if department.parent else "",
            "children": department.children.all().count(),
        }

    def get_category_display_name(self, instance):
        department = instance.get_map_object()
        return get_category_display_name_map()[department.category_id]


class RecycleBinProfileOutputSlZ(RecycleBinBaseSerializer):
    category_display_name = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    def get_profile(self, instance):
        profile = instance.get_map_object()
        return {
            "id": profile.id,
            "username": f"{profile.username}@{profile.domain}",
            "display_name": profile.display_name,
            "department": profile.departments.values("id", "name"),
        }

    def get_category_display_name(self, instance):
        profile = instance.get_map_object()
        return get_category_display_name_map()[profile.category_id]
