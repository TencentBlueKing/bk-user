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
    """add user_member_of attribute"""
    SettingMeta = apps.get_model("user_settings", "SettingMeta")
    need_connect_types = [CategoryType.MAD.value, CategoryType.LDAP.value]
    new_setting_meta_map = {}
    for category_type in need_connect_types:
        meta, _ = SettingMeta.objects.get_or_create(
            namespace=SettingsEnableNamespaces.FIELDS.value,
            region="group",
            category_type=category_type,
            required=False,
            **dict(key="user_member_of", example="memberOf", default="memberOf")
        )
        new_setting_meta_map[category_type] = meta
    ProfileCategory = apps.get_model("categories", "ProfileCategory")
    Setting = apps.get_model("user_settings", "Setting")

    ldap_mad_categories = ProfileCategory.objects.filter(type__in=need_connect_types)
    for ldap_or_mad_category in ldap_mad_categories:
        new_meta = new_setting_meta_map.get(ldap_or_mad_category.type)
        if new_meta:
            Setting.objects.get_or_create(
                category_id=ldap_or_mad_category.id,
                meta=new_meta,
                value=new_meta.default,
            )


def backwards_func(apps, schema_editor):
    SettingMeta = apps.get_model("user_settings", "SettingMeta")
    need_connect_types = [CategoryType.MAD.value, CategoryType.LDAP.value]
    meta = SettingMeta.objects.filter(
        namespace=SettingsEnableNamespaces.FIELDS.value,
        region="group",
        category_type__in=need_connect_types,
        key="user_member_of",
    )
    Setting = apps.get_model("user_settings", "Setting")
    Setting.objects.filter(category__type__in=need_connect_types, meta__in=meta).delete()
    meta.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("user_settings", "0006_auto_20200429_1540"),
    ]

    operations = [migrations.RunPython(forwards_func, backwards_func)]
