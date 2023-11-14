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
from django.db import migrations


def forwards_func(apps, schema_editor):
    """初始化用户内置字段"""

    UserBuiltinField = apps.get_model("tenant", "UserBuiltinField")
    fields = [
        UserBuiltinField(
            name="username",
            display_name="用户名",
            data_type="string",
            required=True,
            unique=True,
        ),
        UserBuiltinField(
            name="full_name",
            display_name="姓名",
            data_type="string",
            required=True,
            unique=False,
        ),
        UserBuiltinField(
            name="email",
            display_name="邮箱",
            data_type="string",
            required=False,
            unique=False,
        ),
        UserBuiltinField(
            name="phone",
            display_name="手机号",
            data_type="string",
            required=False,
            unique=False,
        ),
        UserBuiltinField(
            name="phone_country_code",
            display_name="手机国际区号",
            data_type="string",
            required=False,
            unique=False,
        ),
    ]
    UserBuiltinField.objects.bulk_create(fields)


class Migration(migrations.Migration):
    dependencies = [
        ("tenant", "0001_initial"),
    ]

    operations = [migrations.RunPython(forwards_func)]
