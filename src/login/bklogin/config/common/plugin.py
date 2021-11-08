# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS
Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from bklogin.config.common.django_basic import INSTALLED_APPS, ROOT_URLCONF

##################
# Login Config   #
##################
# 蓝鲸登录方式：bk_login，自定义登录方式：custom_login
LOGIN_TYPE = "bk_login"
CUSTOM_LOGIN_VIEW = ""
CUSTOM_AUTHENTICATION_BACKEND = ""
try:
    custom_conf_module_path = "bklogin.ee_login.settings_login"

    custom_conf_module = __import__(custom_conf_module_path, globals(), locals(), ["*"])
    LOGIN_TYPE = getattr(custom_conf_module, "LOGIN_TYPE", "bk_login")

    CUSTOM_LOGIN_VIEW = getattr(custom_conf_module, "CUSTOM_LOGIN_VIEW", "")
    CUSTOM_AUTHENTICATION_BACKEND = getattr(custom_conf_module, "CUSTOM_AUTHENTICATION_BACKEND", "")
    # 支持自定义登录 patch 原有的所有URL 和 添加自定义 Application  START
    ROOT_URLCONF = getattr(custom_conf_module, "ROOT_URLCONF", None) or ROOT_URLCONF
    if LOGIN_TYPE == "custom_login":
        INSTALLED_APPS = tuple(  # type: ignore
            list(INSTALLED_APPS)
            + getattr(
                custom_conf_module,
                "CUSTOM_INSTALLED_APPS",
                [],
            )
        )
    # 支持自定义登录 patch 原有的所有URL 和 添加自定义 Application  END
except ImportError as e:
    print("load custom_login settings fail!", e)
    LOGIN_TYPE = "bk_login"
