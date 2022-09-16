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


class SearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField()
    max_items = serializers.IntegerField(required=False)

    # page = serializers.IntegerField(required=False, default=1)
    # page_size = serializers.IntegerField(required=False, default=10)
    # no_page = serializers.BooleanField(default=False)


# class SearchResultProfileLeaderSerializer(serializers.Serializer):
#     id = serializers.IntegerField(required=False, read_only=True)
#     username = serializers.CharField()
#     display_name = serializers.CharField(read_only=True)


# class SearchResultProfileDepartmentSerializer(serializers.Serializer):
#     id = serializers.IntegerField(required=False)
#     name = serializers.CharField(required=False)
#     full_name = serializers.CharField(required=False)
#     category_id = serializers.IntegerField(required=False)


class SearchResultProfileOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    username = serializers.CharField(required=True)
    display_name = serializers.CharField(required=True)

    category_id = serializers.IntegerField()
    category_name = serializers.SerializerMethodField(required=False)

    # departments = SearchResultProfileDepartmentSerializer(many=True, required=False, help_text="部门列表")
    # leaders = SearchResultProfileLeaderSerializer(many=True, required=False, help_text="上级列表", source="leader")

    def get_category_name(self, obj):
        return get_category_display_name_map().get(obj.category_id, obj.category_id)


class SearchResultDepartmentOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    full_name = serializers.CharField()

    category_id = serializers.IntegerField()
    category_name = serializers.SerializerMethodField(required=False)

    def get_category_name(self, obj):
        return get_category_display_name_map().get(obj.category_id, obj.category_id)


class SearchResultOutputSLZ(serializers.Serializer):
    type = serializers.CharField()
    display_name = serializers.CharField()
    items = serializers.ListField(help_text="Profile 或 Department 对象列表，请直接参考模型定义")
