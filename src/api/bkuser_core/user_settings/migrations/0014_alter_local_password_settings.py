# Generated by Django 3.2.13 on 2022-06-06 06:58
from __future__ import unicode_literals

from django.db import migrations

from bkuser_core.categories.constants import CategoryType
from bkuser_core.user_settings.constants import SettingsEnableNamespaces


def forwards_func(apps, schema_editor):
    """添加默认用户目录"""
    SettingMeta = apps.get_model("user_settings", "SettingMeta")

    local_password_settings = [
        dict(
            key="init_mail_config",
            default={
                "title": "蓝鲸智云 - 您的账户已经成功创建！",
                "sender": "蓝鲸智云",
                "content": "您好！您的蓝鲸智云账户已经成功创建，以下是您的账户信息:登录账户：{username}， "
                "初始登录密码：{password} 为了保障账户安全，我们建议您尽快登录蓝鲸智云修改密码：{url} "
                "此邮件为系统自动发送，请勿回复。蓝鲸智云官网： http://bk.tencent.com",
            },
        ),
        dict(
            key="reset_mail_config",
            default={
                "title": "蓝鲸智云 - 登录密码重置",
                "sender": "蓝鲸智云",
                "content": "您好！我们收到了你重置密码的申请，请点击下方链接进行密码重置：{url} "
                "该链接有效时间为3小时，过期后请重新点击密码重置链接：{reset_url} 此邮件为系统自动发送，请勿回复",
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
        except Exception as e:
            print("update local password settings fail: key={}, error={}".format(x["key"], e))


class Migration(migrations.Migration):

    dependencies = [
        ("user_settings", "0013_auto_20220511_1507"),
    ]

    operations = [migrations.RunPython(forwards_func)]
