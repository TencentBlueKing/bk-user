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

from django.db import migrations


def forwards_func(apps, schema_editor):
    UserBuiltinField = apps.get_model("tenant", "UserBuiltinField")

    # 更新邮箱字段的 required 属性默认为 True
    UserBuiltinField.objects.filter(name="email").update(required=True)


class Migration(migrations.Migration):
    dependencies = [
        ("tenant", "0010_virtualuserownerrelation_virtualuserapprelation"),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
