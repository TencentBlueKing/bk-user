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


class SubDepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    order = serializers.IntegerField(required=False)
    full_name = serializers.CharField(required=False)
    has_children = serializers.BooleanField(required=False)


class DepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    order = serializers.IntegerField(required=False)
    enabled = serializers.BooleanField(required=False)
    full_name = serializers.CharField()
    children = SubDepartmentSerializer(many=True, required=False)
    ancestors = SubDepartmentSerializer(many=True, required=False)
    has_children = serializers.BooleanField(required=False)
    category_id = serializers.IntegerField()
    category_name = serializers.CharField(required=False)


class DepartmentListSerializer(serializers.Serializer):
    level = serializers.IntegerField(default=0)
    only_enabled = serializers.BooleanField(default=True)


class DepartmentSearchSerializer(serializers.Serializer):
    keyword = serializers.CharField(allow_blank=False)
    with_ancestors = serializers.BooleanField(default=False)
    max_items = serializers.IntegerField(required=False, default=10)


class DepartmentProfileSerializer(serializers.Serializer):
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=10)
    recursive = serializers.BooleanField(default=True)
    keyword = serializers.CharField(required=False)


class ListDepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    profile_count = serializers.IntegerField()
    departments = DepartmentSerializer(many=True)


class UpdateDepartmentSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    order = serializers.IntegerField(required=False)


class DepartmentAddProfilesSerializer(serializers.Serializer):
    profile_id_list = serializers.ListField(child=serializers.IntegerField())
