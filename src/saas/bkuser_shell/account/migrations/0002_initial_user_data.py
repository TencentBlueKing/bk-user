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

from django.conf import settings
from django.db import migrations


def initial_user_data(apps, schema_editor):
    BkUser = apps.get_model("account", "BkUser")
    try:
        admin_username_list = settings.ADMIN_USERNAME_LIST
        for username in admin_username_list:
            BkUser.objects.create_superuser(username)
    except Exception as e:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(initial_user_data),
    ]