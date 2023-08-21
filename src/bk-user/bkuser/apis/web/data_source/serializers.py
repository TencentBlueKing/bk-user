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
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from bkuser.apps.data_source.models import DataSourceDepartmentUserRelation, DataSourceUser


class DataSourceSearchDepartmentsOutputSchema(serializers.Serializer):
    id = serializers.CharField(help_text="部门ID")
    name = serializers.CharField(help_text="部门名称")


class UserSearchInputSLZ(serializers.Serializer):
    username = serializers.CharField(required=False, help_text="用户名", allow_blank=True)


@swagger_serializer_method(serializer_or_field=DataSourceSearchDepartmentsOutputSchema(many=True))
class UserSearchOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户ID")
    username = serializers.CharField(help_text="用户名")
    full_name = serializers.CharField(help_text="全名")
    phone = serializers.CharField(help_text="手机号")
    email = serializers.CharField(help_text="邮箱")
    departments = serializers.SerializerMethodField(help_text="用户部门")

    # TODO:考虑抽象一个函数 获取数据后传递到context
    def get_departments(self, obj: DataSourceUser):
        return [
            {"id": department_user_relation.department.id, "name": department_user_relation.department.name}
            for department_user_relation in DataSourceDepartmentUserRelation.objects.filter(user=obj)
        ]
