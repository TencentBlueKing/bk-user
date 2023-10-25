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
import datetime
import logging
import random
import string
import time
from typing import Tuple
from urllib.parse import unquote

from blue_krill.encrypt.handler import EncryptHandler
from django.conf import settings
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _

from .models import BkToken

logger = logging.getLogger(__name__)


class BkTokenProcessor:
    """
    BKToken处理
    生成并加密Token & 解密Token
    """

    def __init__(self, encrypt_secret_key: bytes):
        # Token加密密钥
        self.encrypt_secret_key = encrypt_secret_key

    @staticmethod
    def _salt(length: int = 8) -> str:
        """生成长度为length 的随机字符串"""
        allow_chars = string.ascii_letters + string.digits
        return "".join([random.choice(allow_chars) for __ in range(length)])

    def generate(self, username: str, expires: int) -> str:
        """token生成"""
        # 加盐
        plain_token = "%s|%s|%s" % (expires, username, self._salt())

        # 加密
        return EncryptHandler(secret_key=self.encrypt_secret_key).encrypt(plain_token)

    def parse(self, bk_token: str) -> Tuple[str, int]:
        """token解析"""
        try:
            plain_bk_token = EncryptHandler(secret_key=self.encrypt_secret_key).decrypt(bk_token)
        except Exception:
            logger.exception("参数[%s] 解析失败", bk_token)
            plain_bk_token = ""

        error_msg = _("参数 bk_token 非法")
        if not plain_bk_token:
            raise ValueError(error_msg)

        try:
            token_info = plain_bk_token.split("|")
        except Exception:
            logger.exception("分割 bk_token[%s] 失败", bk_token)
            raise ValueError(error_msg)

        if not token_info or len(token_info) < 3:  # noqa: PLR2004
            raise ValueError(error_msg)

        return token_info[1], int(token_info[0])


class BkTokenManager:
    def __init__(self):
        # Token加密密钥
        self.bk_token_processor = BkTokenProcessor(encrypt_secret_key=force_bytes(settings.ENCRYPT_SECRET_KEY))
        # Token 过期间隔
        self.cookie_age = settings.BK_TOKEN_COOKIE_AGE
        # Token 无操作失效间隔
        self.inactive_age = settings.BK_TOKEN_INACTIVE_AGE
        # Token 校验时间允许误差
        self.offset_error_age = settings.BK_TOKEN_OFFSET_ERROR_AGE

        # Token生成失败的重试次数
        self.allowed_retry_count = 5

    def get_bk_token(self, username: str) -> Tuple[str, datetime.datetime]:
        """
        生成用户的登录态
        """
        bk_token = ""
        expire_time = int(time.time())
        # 重试5次
        retry_count = 0
        while not bk_token and retry_count < self.allowed_retry_count:
            now_time = int(time.time())
            # Token过期时间
            expire_time = now_time + self.cookie_age
            # Token 无操作失效时间
            inactive_expire_time = now_time + self.inactive_age
            # 生成bk_token
            bk_token = self.bk_token_processor.generate(username, expire_time)
            # DB记录
            try:
                BkToken.objects.create(token=bk_token, inactive_expire_time=inactive_expire_time)
            except Exception:  # noqa: PERF203
                logger.exception("Login ticket failed to be saved during ticket generation")
                # 循环结束前将bk_token置空后重新生成
                bk_token = "" if retry_count + 1 < self.allowed_retry_count else bk_token
            retry_count += 1

        return bk_token, datetime.datetime.fromtimestamp(expire_time, timezone.get_current_timezone())

    def is_bk_token_valid(self, bk_token: str) -> Tuple[bool, str, str]:
        """
        验证用户登录态
        """
        if not bk_token:
            return False, "", _("参数 bk_token 缺失")

        bk_token = unquote(bk_token)
        # 解析bk_token获取username和过期时间
        try:
            username, expire_time = self.bk_token_processor.parse(bk_token)
        except ValueError as error:
            return False, "", str(error)

        # 检查DB是存在
        try:
            bk_token_obj = BkToken.objects.get(token=bk_token)
            is_logout = bk_token_obj.is_logout
            inactive_expire_time = bk_token_obj.inactive_expire_time
        except Exception:
            return False, "", _("不存在 bk_token[%s] 的记录").format(bk_token)

        # token已注销
        if is_logout:
            return False, "", _("登录态已注销")

        now_time = int(time.time())
        # token有效期已过
        if now_time > expire_time + self.offset_error_age:
            return False, "", _("登录态已过期")

        # token有效期大于当前时间的有效期
        if expire_time - now_time > self.cookie_age + self.offset_error_age:
            return False, "", _("登录态有效期不合法")

        # token 无操作有效期已过
        if now_time > inactive_expire_time + self.inactive_age:
            return False, "", _("长时间无操作，登录态已过期")

        # 更新 无操作有效期
        try:
            BkToken.objects.filter(token=bk_token).update(inactive_expire_time=now_time + self.inactive_age)
        except Exception:
            logger.exception("update inactive_expire_time fail")

        return True, username, ""
