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


class DepartmentProfileRelationListInputSLZ(serializers.Serializer):
    no_page = serializers.BooleanField(help_text="全量返回", default=False)


class DepartmentProfileRelationListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="关联 ID")
    department_id = serializers.IntegerField(help_text="租户部门 ID")
    profile_id = serializers.CharField(help_text="租户用户 ID")


class ProfileLeaderRelationListInputSLZ(serializers.Serializer):
    no_page = serializers.BooleanField(help_text="全量返回", default=False)


class ProfileLeaderRelationListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="关联 ID")
    from_profile_id = serializers.CharField(help_text="租户用户 ID")
    to_profile_id = serializers.CharField(help_text="租户用户 Leader ID")
