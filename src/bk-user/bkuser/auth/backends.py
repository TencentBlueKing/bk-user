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
import traceback

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.db import IntegrityError

from bkuser.component import login

logger = logging.getLogger("app")


class TokenBackend(BaseBackend):
    def authenticate(self, request=None, bk_token=None):
        logger.debug("Enter in TokenBackend")
        # 判断是否传入验证所需的bk_token,没传入则返回None
        if not bk_token:
            return None

        verify_result, username = self.verify_bk_token(bk_token)
        # 判断bk_token是否验证通过,不通过则返回None
        if not verify_result:
            return None

        user_model = get_user_model()

        try:
            user, _ = user_model.objects.get_or_create(username=username)
            get_user_info_result, user_info = self.get_user_info(bk_token)
            # 判断是否获取到用户信息,获取不到则返回None
            if not get_user_info_result:
                return None
            user.set_property(key="language", value=user_info.get("language", ""))
            user.set_property(key="time_zone", value=user_info.get("time_zone", ""))
            user.set_property(key="tenant_id", value=user_info.get("tenant_id", ""))

            return user

        except IntegrityError:
            logger.exception(traceback.format_exc())
            logger.exception("get_or_create UserModel fail or update_or_create UserProperty")
            return None
        except Exception:  # pylint: disable=broad-except
            logger.exception(traceback.format_exc())
            logger.exception("Auto create & update UserModel fail")
            return None

    @staticmethod
    def get_user_info(bk_token):
        """
        请求平台ESB接口获取用户信息
        @param bk_token: bk_token
        @type bk_token: str
        @return:True, {
            'username': 'test',
            'language': 'zh-cn',
            'time_zone': 'Asia/Shanghai',
        }
        @rtype: bool,dict
        """
        try:
            data = login.get_user_info(bk_token)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Abnormal error in get_user_info, bk_token=%s", bk_token)
            return False, {}

        user_info = {
            "username": data.get("bk_username", ""),
            "language": data.get("language", ""),
            "time_zone": data.get("time_zone", ""),
            "tenant_id": data.get("tenant_id", ""),
        }
        return True, user_info

    @staticmethod
    def verify_bk_token(bk_token):
        """
        请求VERIFY_URL,认证bk_token是否正确
        @param bk_token: "_FrcQiMNevOD05f8AY0tCynWmubZbWz86HslzmOqnhk"
        @type bk_token: str
        @return: False,None True,username
        @rtype: bool,None/str
        """
        try:
            data = login.verify_bk_token(bk_token)
        except Exception:  # pylint: disable=broad-except
            logger.warning("Abnormal error in verify_bk_token...", exc_info=True)
            return False, None

        return True, data["bk_username"]
