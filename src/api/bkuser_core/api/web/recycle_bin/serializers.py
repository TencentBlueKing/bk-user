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
from bkuser_core.profiles.models import Profile
from bkuser_core.recycle_bin.models import RecycleBin


class RecycleBinSearchInputSlZ(serializers.Serializer):
    keyword = serializers.CharField(required=False, help_text="搜索关键词")


class RecycleBinCategoryOutputSlZ(serializers.ModelSerializer):
    category = serializers.SerializerMethodField(help_text="目录基础信息")
    profile_count = serializers.SerializerMethodField(help_text="目录下人员数量")
    department_count = serializers.SerializerMethodField(help_text="目录下部门数量")
    expires = serializers.IntegerField(help_text="过期剩余天数")

    def get_category(self, instance):
        category = self.context["category_map"][instance.object_id]
        return {
            "id": category.id,
            "display_name": category.display_name,
            "domain": category.domain,
            "type": category.type,
        }

    def get_profile_count(self, instance):
        return Profile.objects.filter(category_id=instance.object_id).count()

    def get_department_count(self, instance):
        return Department.objects.filter(category_id=instance.object_id).count()

    class Meta:
        model = RecycleBin
        fields = ["id", "expires", "category", "profile_count", "department_count", "operator"]


class RecycleBinDepartmentOutputSlZ(serializers.ModelSerializer):
    category_display_name = serializers.SerializerMethodField(help_text="所属目录名称")
    department = serializers.SerializerMethodField(help_text="部门基础信息")
    profile_count = serializers.SerializerMethodField(help_text="部门下人员数量")
    expires = serializers.IntegerField(help_text="过期剩余天数")

    def get_department(self, instance):
        department = self.context["department_map"][instance.object_id]
        return {
            "id": department.id,
            "name": department.name,
            "parent_name": department.parent.name if department.parent else "",
            "children_count": department.children.all().count(),
        }

    def get_category_display_name(self, instance):
        department = self.context["department_map"][instance.object_id]
        return self.context["category_display_name_map"][department.category_id]

    def get_profile_count(self, instance):
        return self.context["department_map"][instance.object_id].profiles.count()

    class Meta:
        model = RecycleBin
        fields = ["id", "expires", "category_display_name", "department", "profile_count", "operator"]


class RecycleBinProfileOutputSlZ(serializers.ModelSerializer):
    category_display_name = serializers.SerializerMethodField(help_text="所属目录信息")
    profile = serializers.SerializerMethodField(help_text="人员基础信息")
    expires = serializers.IntegerField(help_text="过期剩余天数")

    def get_profile(self, instance):
        profile = self.context["profile_map"][instance.object_id]
        return {
            "id": profile.id,
            "username": profile.username,
            "domain": profile.domain,
            "display_name": profile.display_name,
            "department": profile.departments.values("id", "name"),
        }

    def get_category_display_name(self, instance):
        profile = self.context["profile_map"][instance.object_id]
        return self.context["category_display_name_map"][profile.category_id]

    class Meta:
        model = RecycleBin
        fields = ["id", "expires", "category_display_name", "profile", "operator"]
