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
    """更新默认目录 密码-rsa加密模板配置"""
    SettingMeta = apps.get_model("user_settings", "SettingMeta")

    local_password_rsa_settings = [
        dict(
            key="enable_password_rsa_encrypted",
            default=False,
            example=False
        ),
        dict(
            key="password_rsa_private_key",
            default="",
            example="LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpkZnNkZmRzZgotLS0tLUVORCBSU0EgUFJJVkFURSBLRVktLS0tLQo="
        ),
        dict(
            key="password_rsa_public_key",
            default="",
            example="LS0tLS1CRUdJTiBSU0EgUFVCTElDS0VZLS0tLS0KZXJ0ZXJ0cmV0Ci0tLS0tRU5EIFJTQSBQVUJMSUNLRVktLS0tLQo="
        )
    ]

    for x in local_password_rsa_settings:

        meta, _ = SettingMeta.objects.get_or_create(
            namespace=SettingsEnableNamespaces.PASSWORD.value,
            category_type=CategoryType.LOCAL.value,
            required=False,
            **x
        )


class Migration(migrations.Migration):
    dependencies = [
        ("user_settings", "0018_alter_local_password_mail_config"),
    ]

    operations = [migrations.RunPython(forwards_func)]
