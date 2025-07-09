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
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from .utils import get_access_token, get_user_id_by_code, get_user_info_by_userid
from bklogin.common import usermgr
from bklogin.common.log import logger


class WecomQrBackend(ModelBackend):
    """
    企业微信扫码登录认证方法

    注意: 打logger.debug用于调试, 可以在日志路径下login.log查看到对应日志
    """

    def authenticate(self, request, code=None, **kwargs):
        # 企业微信扫码登录验证
        logger.debug("WecomQrBackend authenticate, code=%s", code)
        try:
            if not code:
                logger.debug("no code provided")
                return None

            # 首先获取 access_token
            access_token = get_access_token()
            if not access_token:
                logger.debug("WecomQrBackend get_access_token fail")
                return None

            # 通过 access_token 和 code 获取用户微信 ID
            user_id = get_user_id_by_code(access_token, code)
            if not user_id:
                logger.debug("WecomQrBackend get_user_id_by_code fail")
                return None

            logger.debug("WecomQrBackend get user_id=%s", user_id)

            # 通过 access_token 和 user_id 获取用户信息
            user_info = get_user_info_by_userid(access_token, user_id)
            if not user_info:
                logger.debug("WecomQrBackend: no user_info in user_info")
                return None

            # 企业微信的 `别名` 就是用户管理系统中的 username
            username = user_info.get("alias")

            # 先检查用户管理系统中是否已经存在该用户
            logger.debug("WechatQrBackend: checking if user exists in usermgr, username=%s", username)
            ok, message, user = usermgr.get_user(username)
            if not ok:
                logger.info("WechatQrBackend: user not found in usermgr, username=%s, message=%s", username, message)
                # 用户不存在，说明还没有从企业微信同步到用户管理系统
                return None

            # 用户存在，检查用户状态
            logger.debug("WechatQrBackend: user found in usermgr, user=%s", user)

            # TODO: 根据用户状态判断是否登陆成功
            # 用户存在且状态正常，构造用户信息
            UserModel = get_user_model()
            user = UserModel()
            user.username = username

            logger.info("WecomQrBackend login success for existing user: %s", username)
            return user

        except Exception:
            logger.exception("WecomQrBackend login backend validation error!")
            return None
