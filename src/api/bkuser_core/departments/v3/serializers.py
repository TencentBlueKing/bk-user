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
from bkuser_core.apis.v3.serializers import StringArrayField
from rest_framework.serializers import CharField, IntegerField, Serializer


class DepartmentSerializer(Serializer):
    id = IntegerField(required=False)
    name = CharField(required=False)
    full_name = CharField(required=False)
    category_id = IntegerField(required=False)

    class Meta:
        ref_name = "v3_department"


# ------------
# Request
# ------------
class QueryDeptSerializer(DepartmentSerializer):
    ordering = CharField(required=False, help_text="排序字段", default="id")
    cursor = CharField(required=False, help_text="游标")
    # 暂不支持 fields 限制返回字段
    # fields = StringArrayField(required=False, help_text="返回字段")
    parent = StringArrayField(required=False, help_text="父节点列表")
    children = StringArrayField(required=False, help_text="子节点列表")

    name__in = StringArrayField(required=False, help_text="部门名称列表")


# ------------
# Response
# ------------


class PaginatedDeptSerializer(Serializer):
    count = IntegerField(required=False, help_text="总数")
    next = CharField(required=False, help_text="下一页游标")
    previous = CharField(required=False, help_text="上一页游标")
    results = DepartmentSerializer(many=True, help_text="结果")
