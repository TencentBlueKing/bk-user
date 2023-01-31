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
    Setting = apps.get_model("user_settings", "Setting")
    ProfileCategory = apps.get_model("categories", "ProfileCategory")

    local_password_reset_by_phone_settings = [
        dict(
            key="reset_password_sms_config",
            example={
                "sender": "蓝鲸智云",
                "content": "【腾讯蓝鲸】验证码：{verification_code}您正在重置密码，如非本人操作，请忽略该短信",
                "content_html": "<p>蓝鲸验证码：{verification_code}，您正在重置密码，如非本人操作，请忽略该短信</p>"
            },
            default={
                "sender": "蓝鲸智云",
                "content": "【腾讯蓝鲸】验证码：{verification_code}，您正在重置密码，如非本人操作，请忽略该短信",
                "content_html": "<p>蓝鲸验证码：{verification_code}，您正在重置密码，如非本人操作，请忽略该短信</p>"
            },
        ),
        # 最大验证失败次数
        dict(
            key="failed_verification_max_limit",
            example=3,
            default=3,
        ),
        # 每日最多发送次数
        dict(
            key="reset_sms_send_max_limit",
            example=5,
            default=5,
        ),
        # 验证码有效时间
        dict(
            key="verification_code_expire_seconds",
            example=1 * 60,
            default=1 * 60,
        ),
        # 验证码长度
        dict(
            key="verification_code_length",
            example=6,
            default=6,
        )
    ]

    for x in local_password_reset_by_phone_settings:

        meta, _ = SettingMeta.objects.get_or_create(
            namespace=SettingsEnableNamespaces.ACCOUNT.value,
            category_type=CategoryType.LOCAL.value,
            required=False,
            **x
        )
        for category in ProfileCategory.objects.filter(type=CategoryType.LOCAL.value):
            Setting.objects.get_or_create(meta=meta, category_id=category.id, value=meta.default)


class Migration(migrations.Migration):
    dependencies = [
        ("user_settings", "0019_alter_local_password_rsa_config"),
    ]

    operations = [migrations.RunPython(forwards_func)]
