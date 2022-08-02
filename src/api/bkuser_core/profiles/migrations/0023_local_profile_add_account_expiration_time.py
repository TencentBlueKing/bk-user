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
from django.db.models import F

import datetime


def forwards_func(apps, schema_editor):
    """
    本地目录用户增加 账号有效期 字段
    """

    SettingMeta = apps.get_model("user_settings", "SettingMeta")
    Setting = apps.get_model("user_settings", "Setting")
    ProfileCategory = apps.get_model("categories", "ProfileCategory")
    Profile = apps.get_model("profiles", "Profile")

    # 保证已存在的本地目录下用户拥有过期时间
    for c in ProfileCategory.objects.filter(type=CategoryType.LOCAL.value):
        # 获取对应目录下的 账号有效期配置
        meta = SettingMeta.objects.filter(
            key="expired_after_days",
            namespace=SettingsEnableNamespaces.ACCOUNT.value
        ).first()

        expired_after_days = Setting.objects.filter(
            category_id=c.id,
            meta=meta,
        ).first().value

        if expired_after_days == -1:
            Profile.objects.filter(category_id=c.id).update(
                account_expiration_date=datetime.date(year=2100, month=1, day=1))

        # 过期时间=用户创建时间+账号有效期
        else:
            Profile.objects.filter(category_id=c.id).update(
                account_expiration_date=F("create_time")+datetime.timedelta(days=expired_after_days))


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0022_auto_20220520_1028"),
        ("user_settings", "0016_add_default_fields_account_settings")
    ]

    operations = [migrations.RunPython(forwards_func)]
