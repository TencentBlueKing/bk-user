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
from __future__ import unicode_literals

from django.db import migrations

from bkuser_core.user_settings.constants import GlobalSettingsEnableNamespaces


def forwards_func(apps, schema_editor):
    """更新全局配置项 回收站保存时长"""
    GlobalSettings = apps.get_model("user_settings", "GlobalSettings")
    recycling_strategy_config = dict(
        key="retention_days",
        value=30,
        default=30,
        namespace=GlobalSettingsEnableNamespaces.RECYCLING_STRATEGY.value,
        enabled=True,
        choices=[7, 30, 90, 180, 365],
        region="default",
    )
    GlobalSettings.objects.create(**recycling_strategy_config)


def backwards_func(apps, schema_editor):
    GlobalSettings = apps.get_model("user_settings", "GlobalSettings")
    recycling_strategy_config = dict(
        key="retention_days",
        namespace=GlobalSettingsEnableNamespaces.RECYCLING_STRATEGY.value,
    )
    GlobalSettings.objects.filter(**recycling_strategy_config).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("user_settings", "0021_globalsettings"),
    ]

    operations = [migrations.RunPython(forwards_func, backwards_func)]
