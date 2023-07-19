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
from typing import Tuple

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.db import IntegrityError
from django.utils.translation import get_language

from .exceptions import NoPermissionAccessError
from bkuser_shell.account import get_user_model
from bkuser_shell.account.conf import ConfFixture
from bkuser_shell.account.http import send

logger = logging.getLogger(__name__)

ROLE_TYPE_ADMIN = "1"


class TokenBackend(ModelBackend):
    def authenticate(self, request=None, bk_token=None, **kwargs):
        # logger.debug("Going to authenticate by TokenBackend")
        # 判断是否传入验证所需的bk_token,没传入则返回None
        if not bk_token:
            return None

        verify_result, username = self.verify_bk_token(bk_token)
        # 判断bk_token是否验证通过,不通过则返回None
        if not verify_result:
            return None

        try:
            user, _ = get_user_model().objects.get_or_create(username=username)
            get_user_info_result, user_info = self.get_user_info(bk_token)
            # 判断是否获取到用户信息,获取不到则返回None
            if not get_user_info_result:
                return None

            # 用户权限更新,保持与平台同步
            is_admin = True if str(user_info.get("role", "")) == ROLE_TYPE_ADMIN else False
            user.is_superuser = is_admin
            user.is_staff = is_admin
            user.save()
            return user
        except NoPermissionAccessError:
            raise
        except IntegrityError:
            logger.exception("get_or_create UserModel fail or update UserProperty fail. username=%s", username)
            return None
        except Exception:  # pylint: disable=broad-except
            logger.exception("Auto create & update UserModel fail. username=%s", username)
            return None

    @staticmethod
    def get_user_info(bk_token) -> Tuple[bool, dict]:
        """
        请求 Login 服务 get_user 接口获取用户信息
        @param bk_token: bk_token
        @type bk_token: str
        @return:True, {
            'message': u'\u7528\u6237\u4fe1\u606f\u83b7\u53d6\u6210\u529f',
            'code': 0,
            'data': {
                'qq': '',
                'wx_userid': '',
                'language': 'zh-cn',
                'username': 'test',
                'time_zone': 'Asia/Shanghai',
                'role': 2,
                'phone': '11111111111',
                'email': 'test',
                'chname': 'test'
            },
            'result': True,
            'request_id': 'eac0fee52ba24a47a335fd3fef75c099'
        }
        """
        headers = {"Blueking-Language": get_language()}
        api_params = {
            "bk_app_code": settings.APP_ID,
            "bk_app_secret": settings.APP_TOKEN,
            settings.TOKEN_COOKIE_NAME: bk_token,
        }

        try:
            response = send(ConfFixture.USER_INFO_URL, "GET", api_params, headers=headers, verify=False)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Abnormal error in get_user_info: bk_token=%s***", bk_token[:6])
            return False, {}

        if response.get("result") is True or response.get("ret") == 0:
            # 由于登录服务 v1, v2 的 get_user 存在差异,在这里屏蔽字段的差异,返回字段相同的字典
            origin_user_info = response.get("data", "")
            user_info = {}
            for k in ["wx_userid", "language", "time_zone", "phone", "chname", "email", "qq", "role"]:
                user_info[k] = origin_user_info.get(k, "")

            if settings.DEFAULT_BK_API_VER == "v2":
                user_info["username"] = origin_user_info.get("bk_username", "")
            elif settings.DEFAULT_BK_API_VER == "":
                user_info["username"] = origin_user_info.get("username", "")
            return True, user_info

        code = response.get("code")
        # 特殊：用户认证成功，但用户无应用访问权限
        if code == 1302403:
            raise NoPermissionAccessError(response.get("message"))

        logger.error("Failed to Get User Info: error=%s, ret=%s", response.get("message", ""), response)
        return False, {}

    @staticmethod
    def verify_bk_token(bk_token):
        """
        请求VERIFY_URL,认证bk_token是否正确
        @param bk_token: "_FrcQiMNevOD05f8AY0tCynWmubZbWz86HslzmOqnhk"
        @type bk_token: str
        @return: False,None True,username
        @rtype: bool,None/str
        """
        headers = {"Blueking-Language": get_language()}
        api_params = {
            "bk_app_code": settings.APP_ID,
            "bk_app_secret": settings.APP_TOKEN,
            settings.TOKEN_COOKIE_NAME: bk_token,
        }

        try:
            response = send(ConfFixture.VERIFY_URL, "GET", api_params, headers=headers, verify=False)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Abnormal error in verify_bk_token: bk_token=%s***", bk_token[:6])
            return False, None

        if response.get("result") or response.get("ret") == 0:
            data = response.get("data")
            username = data.get("bk_username")
            return True, username

        code = response.get("code")
        # 特殊：用户认证成功，但用户无应用访问权限
        if code == 1302403:
            raise NoPermissionAccessError(response.get("message"))

        logger.error("Fail to verify bk_token, error=%s, ret=%s", response.get("message", "<Unknown issue>"), response)
        return False, None
