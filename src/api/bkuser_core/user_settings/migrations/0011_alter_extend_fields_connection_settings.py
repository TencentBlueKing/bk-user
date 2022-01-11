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

from bkuser_core.categories.constants import CategoryType
from bkuser_core.user_settings.constants import SettingsEnableNamespaces
from django.db import migrations


def forwards_func(apps, schema_editor):
    """更新自定义字段配置"""
    SettingMeta = apps.get_model("user_settings", "SettingMeta")

    extend_fields_connection_settings = [
        dict(key="dynamic_fields_mapping", default={})
    ]

    for x in extend_fields_connection_settings:
        SettingMeta.objects.create(
            namespace=SettingsEnableNamespaces.FIELDS.value,
            category_type=CategoryType.LDAP.value,
            required=True,
            region="extend",
            **x
        )

    for x in extend_fields_connection_settings:
        SettingMeta.objects.create(
            namespace=SettingsEnableNamespaces.FIELDS.value,
            category_type=CategoryType.MAD.value,
            required=True,
            region="extend",
            **x
        )

    SettingMeta = apps.get_model("user_settings", "SettingMeta")
    keys = ["bk_fields", "mad_fields"]
    meta = SettingMeta.objects.filter(key__in=keys)
    Setting = apps.get_model("user_settings", "Setting")
    Setting.objects.filter(meta__in=meta).delete()
    meta.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("user_settings", "0010_auto_20211201_1601"),
    ]

    operations = [migrations.RunPython(forwards_func)]
