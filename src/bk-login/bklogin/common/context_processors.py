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
from django.conf import settings
from django.utils.translation import gettext_lazy as _


def basic_settings(request):
    """
    项目的基础配置，比如SITE_URL/STATIC_URL等
    """
    return {
        "TITLE": _("蓝鲸登录 | 腾讯蓝鲸智云"),
        "AJAX_BASE_URL": settings.AJAX_BASE_URL.rstrip("/"),
        "SITE_URL": settings.SITE_URL.rstrip("/"),
        "BK_STATIC_URL": settings.STATIC_URL.rstrip("/"),
        "BK_DOMAIN": settings.BK_DOMAIN,
        # CSRF TOKEN COOKIE NAME
        "CSRF_COOKIE_NAME": settings.CSRF_COOKIE_NAME,
    }
