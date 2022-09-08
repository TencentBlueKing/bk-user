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


from enum import Enum
from typing import Optional

from django.utils.translation import ugettext_lazy as _


class LoginErrorCodes(Enum):
    # E1302000_DEFAULT_CODE = 1302000
    E1302001_BASE_SETTINGS_ERROR = 1302001
    E1302002_BASE_DATABASE_ERROR = 1302002
    # E1302003_BASE_HTTP_DEPENDENCE_ERROR=1302003,
    # E1302004_BASE_BKSUITE_DATABASE_ERROR=1302004,
    # E1302005_BASE_LICENSE_ERROR=1302005,
    # E1302006_ENTERPRISE_LOGIN_ERROR=1302006,


class AuthenticationError(Exception):
    message = "login error"
    redirect_to = ""

    def __init__(self, message=None, redirect_to=None):
        if message is not None:
            self.message = message
        if redirect_to is not None:
            self.redirect_to = redirect_to


class PasswordNeedReset(Exception):
    """Auth failure due to needing reset of password"""

    def __init__(self, reset_password_url: str, message: Optional[str] = None):
        self.reset_password_url = reset_password_url
        self.message = message or _("登录校验失败，请重置密码")


class UserExpiredException(Exception):
    """Auth failure due to user had expired"""

    redirect_to = ""

    def __init__(self, redirect_to=None):
        self.user_expired = True
        if redirect_to:
            self.redirect_to = redirect_to
