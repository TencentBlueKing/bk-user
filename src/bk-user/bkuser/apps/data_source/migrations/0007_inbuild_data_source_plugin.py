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
from django.conf import settings
from django.db import migrations

from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.utils.base64 import load_image_as_base64


def forwards_func(apps, schema_editor):
    """初始化通用数据源插件"""

    DataSourcePlugin = apps.get_model("data_source", "DataSourcePlugin")
    if DataSourcePlugin.objects.filter(id=DataSourcePluginEnum.GENERAL).exists():
        return

    # TODO 插件名称，描述国际化
    DataSourcePlugin.objects.create(
        id=DataSourcePluginEnum.GENERAL,
        name=DataSourcePluginEnum.get_choice_label(DataSourcePluginEnum.GENERAL),
        description="支持对接通用 HTTP 数据源的插件，用户需要在服务方提供 `用户数据` 及 `部门数据` API",
        logo=load_image_as_base64(settings.BASE_DIR / "bkuser/plugins/general/logo.png"),
    )


class Migration(migrations.Migration):

    dependencies = [
        ('data_source', '0006_departmentrelationmptttree'),
    ]

    operations = [
        migrations.RunPython(forwards_func)
    ]
