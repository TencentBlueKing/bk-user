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
from typing import Tuple

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from bklogin.backends.constants import BkUserCheckCodeEnum
from bklogin.common.exceptions import AuthenticationError, PasswordNeedReset, UserExpiredException
from bklogin.common.log import logger
from bklogin.common.usermgr import get_categories_str
from bklogin.components import usermgr_api


def _split_username(username):
    """
    admin => ("admin", "")
    admin@123.com => ("admin", "123.com")
    admin@123.com@456.com => ("admin@123.com", "145.com")
    """
    if "@" not in username:
        return username, ""
    parts = username.split("@")
    length = len(parts)
    if length == 2:
        return parts[0], parts[1]
    return "@".join(parts[: length - 1]), parts[length - 1]


class BkUserBackend(ModelBackend):
    """
    蓝鲸用户管理提供的认证
    """

    def _parse_username(self, username: str) -> Tuple[str, str]:
        """
        parse the username, return the username and domain
        """
        domain_list = get_categories_str().split(";")

        s_username, s_domain = _split_username(username)
        logger.debug(
            "the domain_list is %s, and the parsed domain in the list: %s", domain_list, s_domain in domain_list
        )
        if s_domain in domain_list:
            username, domain = s_username, s_domain
        else:
            domain = ""

        logger.debug("parse the domain from username, result: username=%s, domain=%s", username, domain)
        return username, domain

    def authenticate(self, request, username=None, password=None, **kwargs):
        # NOTE: username here maybe: username/phone/email
        if not username or not password:
            if password:
                password = password[:4] + "***"
            logger.debug("username or password empty, username=%s, password=%s", username, password)
            return None

        username, domain = self._parse_username(username)
        # 调用用户管理接口进行验证
        ok, code, message, extra_values = usermgr_api.authenticate(username, password, domain=domain)
        logger.debug(
            "usermgr_api.authenticate result: ok=%s, code=%s, message=%s, extra_values=%s",
            ok,
            code,
            message,
            extra_values,
        )

        # 认证不通过
        if not ok:
            if code in [
                BkUserCheckCodeEnum.SHOULD_CHANGE_INITIAL_PASSWORD.value,
                BkUserCheckCodeEnum.PASSWORD_EXPIRED.value,
            ]:
                raise PasswordNeedReset(message=message, reset_password_url=extra_values.get("reset_password_url"))
            elif code == BkUserCheckCodeEnum.USER_IS_EXPIRED.value:
                raise UserExpiredException
            raise AuthenticationError(message=message, redirect_to=extra_values.get("redirect_to"))

        # set the username to real username
        username = extra_values.get("username", username)
        UserModel = get_user_model()
        user = UserModel(username)

        user.fill_with_userinfo(extra_values)
        return user
