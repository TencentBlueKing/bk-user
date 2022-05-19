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
import logging
from collections import namedtuple

from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import BasicAuthentication

from bkuser_core.bkiam.helper import IAMHelper

logger = logging.getLogger(__name__)


class IAMBasicAuthentication(BasicAuthentication):
    """针对 IAM 的 Basic Auth 校验器"""

    FIXED_IAM_USERNAME = "bk_iam"

    def authenticate_credentials(self, userid, password, request=None):
        """通过接口获取 token 信息校验"""
        if userid != self.FIXED_IAM_USERNAME:
            logger.warning("bkiam callback basic auth username error")
            raise exceptions.AuthenticationFailed(_("Invalid username/password."))

        try:
            ok, msg, token = IAMHelper().get_token()
        except Exception as e:
            logger.exception("can't get token from bkiam")
            raise exceptions.AuthenticationFailed(_("无法从权限中心获取到鉴权 token, 原因: %s") % e)

        if not ok:
            logger.exception("get token from bkiam fail, %s", msg)
            raise exceptions.AuthenticationFailed(_("无法从权限中心获取到鉴权 token, 原因: %s") % msg)

        if token != password:
            logger.warning(
                "bkiam callback basic auth password error. [token=%s, password=%s]", token[:6], password[:6]
            )
            raise exceptions.AuthenticationFailed(_("Invalid username/password."))

        SimpleUser = namedtuple("SimpleUser", "username,is_authenticated")
        return SimpleUser(userid, True), None
