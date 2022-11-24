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
import base64
import datetime

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from bkuser_shell.account.conf import ConfFixture


def shell(request):
    password_rsa_public_key = base64.b64encode(settings.PASSWORD_RSA_PUBLIC_KEY.encode()).decode()
    enable_password_rsa_encrypted = str(settings.ENABLE_PASSWORD_RSA_ENCRYPTED).lower()

    context = {
        "gettext": _,
        "_": _,
        "LANGUAGE": settings.LANGUAGES,
        "APP_ID": settings.APP_ID,
        "SITE_URL": settings.SITE_URL,
        "AJAX_URL": settings.SITE_URL,
        "TITLE": _("用户管理 | 腾讯蓝鲸智云"),
        # 静态资源
        "STATIC_URL": settings.STATIC_URL,
        "STATIC_VERSION": settings.STATIC_VERSION,
        # 登录跳转链接
        "LOGIN_URL": ConfFixture.LOGIN_URL,
        "LOGIN_PAAS_URL": ConfFixture.LOGIN_PLAIN_URL,
        "BK_PAAS_HOST": f"{settings.BK_PAAS_URL}/app/list/",
        "BK_PLAT_HOST": settings.BK_PAAS_URL,
        "BK_MAIL_GATEWAY": f"{settings.BK_COMPONENT_API_URL}/esb/manager/channel/list/",
        "BK_DOC_URL": settings.BK_DOC_URL,
        # 当前页面，主要为了login_required做跳转用
        "APP_PATH": request.get_full_path(),
        "NOW": datetime.datetime.now(),
        # 静态文件加载目录
        "BK_STATIC_URL": settings.BUILD_STATIC,
        "USERNAME": request.user.username,
        # password encrypted
        "PASSWORD_RSA_PUBLIC_KEY": password_rsa_public_key,
        "ENABLE_PASSWORD_RSA_ENCRYPTED": enable_password_rsa_encrypted,
    }

    return context
