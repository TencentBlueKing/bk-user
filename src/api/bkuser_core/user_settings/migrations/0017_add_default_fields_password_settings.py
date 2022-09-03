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
    """添加本地用户目录密码设置"""

    SettingMeta = apps.get_model("user_settings", "SettingMeta")
    Setting = apps.get_model("user_settings", "Setting")
    ProfileCategory = apps.get_model("categories", "ProfileCategory")

    local_password_settings = [

        dict(
            key="password_expiration_notice_methods",
            example=["send_email"],
            default=["send_email"],
        ),
        dict(
            key="password_expiration_notice_interval",
            example=[1, 7, 15],
            default=[1, 7, 15]
        ),
        dict(
            key="expiring_password_email_config",
            example={
                "title": "【蓝鲸智云】密码到期提醒",
                "sender": "蓝鲸智云",
                "content": "{username}，您好：您的蓝鲸智云平台账号将于{expired_at}天后到期，"
                "为避免影响使用，请尽快登陆平台修改密码。蓝鲸智云平台用户管理处",
                "content_html": '<p style="text-align: left;">{username}，您好：</p><p style="text-align: left;">&nbsp;'
                '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;您的蓝鲸智云平台账号将于<span style="color: rgb(225, 60, 57);">'
                '{expired_at}</span>天后到期，为避免影响使用，请尽快登陆平台修改密码。'
                '</p><p style="text-align: right;">蓝鲸智云平台用户管理处</p>',
            },
            default={
                "title": "【蓝鲸智云】密码到期提醒",
                "sender": "蓝鲸智云",
                "content": "{username}，您好：您的蓝鲸智云平台账号将于{expired_at}天后到期，"
                "为避免影响使用，请尽快登陆平台修改密码。蓝鲸智云平台用户管理处",
                "content_html": '<p style="text-align: left;">{username}，您好：</p><p style="text-align: left;">&nbsp;'
                '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;您的蓝鲸智云平台账号将于<span style="color: rgb(225, 60, 57);">'
                '{expired_at}</span>天后到期，为避免影响使用，请尽快登陆平台修改密码。'
                '</p><p style="text-align: right;">蓝鲸智云平台用户管理处</p>',
            },
        ),
        dict(
            key="expired_password_email_config",
            example={
                "title": "【蓝鲸智云】密码到期提醒",
                "sender": "蓝鲸智云",
                "content": "{username}，您好：您的蓝鲸智云平台密码已过期，为避免影响使用，请尽快登陆平台修改密码。蓝鲸智云平台用户管理处",
                "content_html": '<p style="text-align: left;">{username}，您好：</p><p style="text-align: left;">&nbsp;'
                '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;您的蓝鲸智云平台密码已过期，为避免影响使用，请尽快登陆平台修改密码。</p>'
                '<p style="text-align: right;">蓝鲸智云平台用户管理处</p>',
            },
            default={
                "title": "【蓝鲸智云】密码到期提醒",
                "sender": "蓝鲸智云",
                "content": "{username}，您好：您的蓝鲸智云平台密码已过期，为避免影响使用，请尽快登陆平台修改密码。蓝鲸智云平台用户管理处",
                "content_html": '<p style="text-align: left;">{username}，您好：</p><p style="text-align: left;">&nbsp;'
                '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;您的蓝鲸智云平台密码已过期，为避免影响使用，请尽快登陆平台修改密码。</p>'
                '<p style="text-align: right;">蓝鲸智云平台用户管理处</p>',
            },
        ),
        dict(
            key="expiring_password_sms_config",
            example={
                "sender": "蓝鲸智云",
                "content": "【蓝鲸智云】密码到期提醒！{username}，您好，您的蓝鲸平台密码将于{expired_at}天后到期，为避免影响使用，请尽快"
                "登陆平台修改密码。",
                "content_html": '<p>【蓝鲸智云】密码到期提醒！{username}，您好，您的蓝鲸平台密码将于&nbsp;{expired_at}&nbsp;天后到期，'
                '为避免影响使用，请尽快登陆平台修改密码。</p>',
            },
            default={
                "sender": "蓝鲸智云",
                "content": "【蓝鲸智云】密码到期提醒！{username}，您好，您的蓝鲸平台密码将于{expired_at}天后到期，为避免影响使用，请尽快"
                "登陆平台修改密码。",
                "content_html": '<p>【蓝鲸智云】密码到期提醒！{username}，您好，您的蓝鲸平台密码将于&nbsp;{expired_at}&nbsp;天后到期，'
                '为避免影响使用，请尽快登陆平台修改密码。</p>',
            },
        ),
        dict(
            key="expired_password_sms_config",
            example={
                "sender": "蓝鲸智云",
                "content": "【蓝鲸智云】密码到期提醒！{username}您好！您的蓝鲸智云平台密码已过期，为避免影响使用，请尽快登陆平台修改密码。",
                "content_html": '<p>【蓝鲸智云】密码到期提醒！{username}您好！您的蓝鲸智云平台密码已过期，为避免影响使用，请尽快登陆平台'
                '修改密码。</p>',
            },
            default={
                "sender": "蓝鲸智云",
                "content": "【蓝鲸智云】密码到期提醒！{username}您好！您的蓝鲸智云平台密码已过期，为避免影响使用，请尽快登陆平台修改密码。",
                "content_html": '<p>【蓝鲸智云】密码到期提醒！{username}您好！您的蓝鲸智云平台密码已过期，为避免影响使用，请尽快登陆平台'
                '修改密码。</p>',
            },
        ),

    ]

    for x in local_password_settings:
        meta, _ = SettingMeta.objects.get_or_create(
            namespace=SettingsEnableNamespaces.PASSWORD.value,
            category_type=CategoryType.LOCAL.value,
            required=True,
            **x
        )
        # 保证已存在的目录拥有默认配置
        for c in ProfileCategory.objects.filter(type=CategoryType.LOCAL.value):
            Setting.objects.get_or_create(meta=meta, category_id=c.id, value=meta.default)


def backwards_func(apps, schema_editor):
    SettingMeta = apps.get_model("user_settings", "SettingMeta")
    Setting = apps.get_model("user_settings", "Setting")

    meta_keys = [
        "password_expiration_notice_methods",
        "password_expiration_notice_interval",
        "expiring_password_email_config",
        "expired_password_email_config",
        "expiring_password_sms_config",
        "expired_password_sms_config"
    ]

    for meta_key in meta_keys:
        meta = SettingMeta.objects.get(
            namespace=SettingsEnableNamespaces.PASSWORD.value,
            category_type=CategoryType.LOCAL.value,
            key=meta_key
        )

        Setting.objects.filter(category__type=CategoryType.LOCAL.value, meta=meta).delete()
        meta.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("user_settings", "0016_add_default_fields_account_settings"),
    ]

    operations = [migrations.RunPython(forwards_func, backwards_func)]
