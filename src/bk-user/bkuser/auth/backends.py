# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
import logging
from typing import Dict, Tuple

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

from bkuser.component import login

logger = logging.getLogger("app")


class TokenBackend(BaseBackend):
    def authenticate(self, request=None, bk_token=None):
        logger.debug("Enter in TokenBackend")
        # 判断是否传入验证所需的 bk_token，没传入则返回 None
        if not bk_token:
            return None

        result, user_info = self.get_user_info(bk_token)
        # 判断 bk_token 是否验证通过，不通过则返回 None
        if not result:
            return None

        user_model = get_user_model()
        username = user_info["username"]

        user, _ = user_model.objects.get_or_create(username=username)
        user.set_property(key="language", value=user_info["language"])
        user.set_property(key="time_zone", value=user_info["time_zone"])
        user.set_property(key="tenant_id", value=user_info["tenant_id"])
        user.set_property(key="display_name", value=user_info["display_name"])

        return user

    @staticmethod
    def get_user_info(bk_token: str) -> Tuple[bool, Dict]:
        """
        请求平台 ESB 接口获取用户信息
        :param bk_token: 用户登录凭证
        :return: 是否获取成功，用户信息
        """
        try:
            data = login.get_user_info(bk_token)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Abnormal error in get_user_info, bk_token=%s", bk_token)
            return False, {}

        user_info = {
            "username": data["bk_username"],
            "language": data.get("language", ""),
            "time_zone": data.get("time_zone", ""),
            "tenant_id": data.get("tenant_id", ""),
            "display_name": data.get("display_name", ""),
        }
        return True, user_info
