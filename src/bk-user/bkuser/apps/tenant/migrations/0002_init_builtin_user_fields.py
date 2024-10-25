# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from django.conf import settings
from django.db import migrations


def forwards_func(apps, schema_editor):
    """初始化用户内置字段"""

    UserBuiltinField = apps.get_model("tenant", "UserBuiltinField")
    fields = [
        UserBuiltinField(
            name="username",
            display_name="用户名",
            display_name_zh_cn="用户名",
            display_name_en_us="Username",
            data_type="string",
            required=True,
            unique=True,
        ),
        UserBuiltinField(
            name="full_name",
            display_name="姓名",
            display_name_zh_cn="姓名",
            display_name_en_us="Full Name",
            data_type="string",
            required=True,
            unique=False,
        ),
        UserBuiltinField(
            name="email",
            display_name="邮箱",
            display_name_zh_cn="邮箱",
            display_name_en_us="Email",
            data_type="string",
            required=False,
            unique=False,
        ),
        UserBuiltinField(
            name="phone",
            display_name="手机号",
            display_name_zh_cn="手机号",
            display_name_en_us="Phone Number",
            data_type="string",
            required=False,
            unique=False,
        ),
        UserBuiltinField(
            name="phone_country_code",
            display_name="手机国际区号",
            display_name_zh_cn="手机国际区号",
            display_name_en_us="Phone Country Code",
            data_type="string",
            required=False,
            unique=False,
            default=settings.DEFAULT_PHONE_COUNTRY_CODE,
        ),
    ]
    UserBuiltinField.objects.bulk_create(fields)


class Migration(migrations.Migration):
    dependencies = [
        ("tenant", "0001_initial"),
    ]

    operations = [migrations.RunPython(forwards_func)]
