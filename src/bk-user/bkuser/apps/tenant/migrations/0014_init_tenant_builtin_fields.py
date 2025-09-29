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
    """为现有租户初始化默认的内置字段配置"""

    Tenant = apps.get_model("tenant", "Tenant")
    TenantUserBuiltinField = apps.get_model("tenant", "TenantUserBuiltinField")

    # 获取所有现有租户
    tenants = Tenant.objects.all()

    for tenant in tenants:
        # 为每个租户创建默认的内置字段配置
        builtin_fields = [
            {
                "tenant": tenant,
                "name": "username",
                "display_name": "用户名",
                "data_type": "string",
                "required": True,
                "unique": True,
                "default": "",
                "options": [],
                "personal_center_visible": True,
                "personal_center_editable": False,
                "manager_editable": False,
            },
            {
                "tenant": tenant,
                "name": "full_name",
                "display_name": "姓名",
                "data_type": "string",
                "required": True,
                "unique": False,
                "default": "",
                "options": [],
                "personal_center_visible": True,
                "personal_center_editable": False,
                "manager_editable": True,
            },
            {
                "tenant": tenant,
                "name": "email",
                "display_name": "邮箱",
                "data_type": "string",
                "required": True,
                "unique": False,
                "default": "",
                "options": [],
                "personal_center_visible": True,
                "personal_center_editable": True,
                "manager_editable": True,
            },
            {
                "tenant": tenant,
                "name": "phone",
                "display_name": "手机号",
                "data_type": "string",
                "required": False,
                "unique": False,
                "default": "",
                "options": [],
                "personal_center_visible": True,
                "personal_center_editable": True,
                "manager_editable": True,
            },
            {
                "tenant": tenant,
                "name": "phone_country_code",
                "display_name": "手机国际区号",
                "data_type": "string",
                "required": False,
                "unique": False,
                "default": settings.DEFAULT_PHONE_COUNTRY_CODE,
                "options": [],
                "personal_center_visible": True,
                "personal_center_editable": True,
                "manager_editable": True,
            },
        ]

        # 使用 get_or_create 避免重复创建
        for field in builtin_fields:
            TenantUserBuiltinField.objects.get_or_create(
                tenant=field["tenant"],
                name=field["name"],
                defaults={
                    "display_name": field["display_name"],
                    "data_type": field["data_type"],
                    "required": field["required"],
                    "unique": field["unique"],
                    "default": field["default"],
                    "options": field["options"],
                    "personal_center_visible": field["personal_center_visible"],
                    "personal_center_editable": field["personal_center_editable"],
                    "manager_editable": field["manager_editable"],
                }
            )


class Migration(migrations.Migration):
    dependencies = [
        ("tenant", "0013_tenantuserbuiltinfield"),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
