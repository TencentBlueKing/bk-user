# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.conf import settings
from django.db import migrations


from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.utils.base64 import load_image_as_base64


def forwards_func(apps, schema_editor):
    """初始化本地数据源插件"""

    IdpPlugin = apps.get_model("idp", "IdpPlugin")

    # 本地账密认证源插件
    IdpPlugin.objects.get_or_create(
        id=BuiltinIdpPluginEnum.LOCAL,
        defaults={
            "name": BuiltinIdpPluginEnum.get_choice_label(BuiltinIdpPluginEnum.LOCAL),
            "name_zh_cn": "本地账密",
            "name_en_us": "Local Account Password",
            "description": "使用本地DB数据源提供的用户名和密码进行认证",
            "description_zh_cn": "使用本地DB数据源提供的用户名和密码进行认证",
            "description_en_us": "Authenticate using username and password provided by the local DB data source",
            "logo": load_image_as_base64(settings.BASE_DIR / "bkuser/idp_plugins/local/logo.png"),
        },
    )

    # 企业微信认证源插件
    # TODO 插件名称，描述国际化
    IdpPlugin.objects.get_or_create(
        id=BuiltinIdpPluginEnum.WECOM,
        defaults={
            "name": BuiltinIdpPluginEnum.get_choice_label(BuiltinIdpPluginEnum.WECOM),
            "name_zh_cn": "企业微信",
            "name_en_us": "Wecom",
            "description": "使用腾讯企业微信进行企业身份认证",
            "description_zh_cn": "使用腾讯企业微信进行企业身份认证",
            "description_en_us": "Authenticate using Tencent WeCom for corporate identity authentication",
            "logo": load_image_as_base64(settings.BASE_DIR / "bkuser/idp_plugins/wecom/logo.png"),
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("idp", "0001_initial"),
    ]

    operations = [migrations.RunPython(forwards_func)]
