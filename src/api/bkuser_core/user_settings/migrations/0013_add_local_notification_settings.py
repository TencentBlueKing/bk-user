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
    """添加默认用户目录通知设置"""

    SettingMeta = apps.get_model("user_settings", "SettingMeta")
    Setting = apps.get_model("user_settings", "Setting")
    ProfileCategory = apps.get_model("categories", "ProfileCategory")

    local_notification_settings = [
        dict(
            key="notice_method",
            default=["send_email", "send_sms"]
        ),
        dict(
            key="notice_time",
            default=[1, 7, 15]
        ),
        dict(
            key="expiring_email_config",
            default={
                "title": "【蓝鲸智云企业版】密码到期提醒",
                "sender": "蓝鲸智云企业版",
                "content": "{username}，您好！您的蓝鲸智云企业版平台密码将于{expire_at}天后到期，"
                "为避免影响使用，请尽快登陆平台（{url}）修改密码。蓝鲸智云平台用户管理处",
            }
        ),
        dict(
            key="expired_email_config",
            default={
                "title": "【蓝鲸智云企业版】密码到期提醒",
                "sender": "蓝鲸智云企业版",
                "content": "{username}，您好！您的蓝鲸智云企业版平台密码已过期，为避免影响使用，"
                           "请尽快登陆平台（{url}）修改密码。蓝鲸智云平台用户管理处",
            },
        ),
        dict(
            key="expiring_sms_config",
            default={
                "sender": "蓝鲸智云企业版",
                "content": "【蓝鲸智云企业版】密码到期提醒！{username}，您好，您的蓝鲸平台密码将于{expire_at}天后到期，"
                           "为避免影响使用，请尽快登陆平台（{url}）修改密码。"
            },
        ),
        dict(
            key="expired_sms_config",
            default={
                "sender": "蓝鲸智云企业版",
                "content": "【蓝鲸智云企业版】密码到期提醒！{username}您好！您的蓝鲸智云企业版平台密码已过期，"
                           "为避免影响使用，请尽快登陆平台（{url}）修改密码。",
            },
        ),

    ]

    for x in local_notification_settings:
        meta = SettingMeta.objects.create(
            namespace=SettingsEnableNamespaces.NOTIFICATION.value,
            category_type=CategoryType.LOCAL.value,
            required=True,
            **x
        )
        # 保证已存在的目录拥有默认配置
        for c in ProfileCategory.objects.filter(type=CategoryType.LOCAL.value):
            Setting.objects.get_or_create(meta=meta, category_id=c.id, value=meta.default)


def backwards_func(apps, schema_editor):
    SettingMeta = apps.get_model("user_settings", "SettingMeta")
    meta = SettingMeta.objects.get(
        namespace=SettingsEnableNamespaces.NOTIFICATION.value,
        category_type=CategoryType.LOCAL.value
    )
    Setting = apps.get_model("user_settings", "Setting")
    Setting.objects.filter(category__type=CategoryType.LOCAL.value, meta=meta).delete()
    meta.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("user_settings", "0012_auto_20220223_1108"),
    ]

    operations = [migrations.RunPython(forwards_func, backwards_func)]
