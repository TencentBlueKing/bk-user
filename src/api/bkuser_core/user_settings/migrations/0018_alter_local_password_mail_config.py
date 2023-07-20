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
    """更新默认目录 密码-初始化密码通知模板配置"""
    SettingMeta = apps.get_model("user_settings", "SettingMeta")
    Setting = apps.get_model("user_settings", "Setting")

    local_password_settings = [
        dict(
            key="init_mail_config",
            default={
                "title": "蓝鲸智云 - 您的账户已经成功创建！",
                "sender": "蓝鲸智云",
                "content": "您好！您的蓝鲸智云账户已经成功创建，以下是您的账户信息:登录账户：{username}， "
                "初始登录密码：{password} 为了保障账户安全，我们建议您尽快登录蓝鲸智云修改密码：{url} "
                "此邮件为系统自动发送，请勿回复。蓝鲸智云官网： http://bk.tencent.com",
                "content_html": '<p>您好∶</p><p><br></p><p>您的蓝鲸智云账户已经成功创建，以下是您的账户信息'
                '</p><p>登录账户：{username}，初始登录密码：{password}</p><p>为了保障账户安全，我们建议您尽快'
                '登录平台修改密码：{<a href="url" target="_blank">url</a>}</p><p><br></p><p>此邮件为系统'
                '自动发送，请勿回复。蓝鲸智云官网:&nbsp;<a href="http://bk.tencent.com" target="_blank">'
                'http://bk.tencent.com</a></p>'
            },
        ),

        dict(
            key="reset_mail_config",
            default={
                "title": "蓝鲸智云 - 登录密码重置",
                "sender": "蓝鲸智云",
                "content": "您好！我们收到了你重置密码的申请，请点击下方链接进行密码重置：{url} "
                "该链接有效时间为3小时，过期后请重新点击密码重置链接：{reset_url} 此邮件为系统自动发送，请勿回复",
                "content_html": '<p>您好：</p><p><br></p><p>我们收到了您重置密码的申请，请点击下方链接进行密'
                '码重置：{<a href="url" target="_blank">url</a>}</p><p>该链接有效时间为&nbsp;<span style'
                '="color: rgb(225, 60, 57);">3&nbsp;小时</span>，过期后请重新点击密码重置链接：{<a href='
                '"reset_url" target="_blank">reset_url</a>}</p><p><br></p><p>此邮件为系统自动发送，请勿'
                '回复。</p>'

            },
        ),
    ]

    for x in local_password_settings:
        try:
            sm = SettingMeta.objects.get(
                key=x["key"], namespace=SettingsEnableNamespaces.PASSWORD.value, category_type=CategoryType.LOCAL.value
            )
            sm.default = x["default"]
            sm.save()

            # 保证已存在的目录 同步更新配置
            settings = Setting.objects.filter(meta=sm)
            for s in settings:
                s.value = sm.default
                s.save()

        except Exception as e:
            print("update local password settings fail: key={}, error={}".format(x["key"], e))


class Migration(migrations.Migration):

    dependencies = [
        ("user_settings", "0017_add_default_fields_password_settings"),
    ]

    operations = [migrations.RunPython(forwards_func)]

