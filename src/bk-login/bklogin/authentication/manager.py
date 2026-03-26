# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
import datetime
import logging
import random
import string
import time
from typing import Tuple
from urllib.parse import quote_plus, unquote_plus

from blue_krill.encrypt.handler import EncryptHandler
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import BkToken

logger = logging.getLogger(__name__)


class BkTokenProcessor:
    """
    BKToken 处理
    生成并加密 Token & 解密 Token
    """

    def __init__(self):
        # 加密器，默认读取 django settings 里配置的加密密钥和加密类
        self.crypter = EncryptHandler()

    @staticmethod
    def _salt(length: int = 8) -> str:
        """生成长度为 length 的随机字符串"""
        allow_chars = string.ascii_letters + string.digits
        return "".join([random.choice(allow_chars) for __ in range(length)])

    def generate(self, user_id: str, expires_at: int) -> str:
        """token 生成"""
        # 加盐
        plain_token = "%s|%s|%s" % (expires_at, user_id, self._salt())

        # 加密
        return self.crypter.encrypt(plain_token)

    def parse(self, bk_token: str) -> Tuple[str, int]:
        """
        token 解析
        :return: user_id, expires_at
        """
        try:
            plain_bk_token = self.crypter.decrypt(bk_token)
        except Exception:
            logger.exception("参数 bk_token [%s] 解析失败", bk_token)
            plain_bk_token = ""

        error_msg = _("参数 bk_token 非法")
        if not plain_bk_token:
            raise ValueError(error_msg)

        try:
            token_info = plain_bk_token.split("|")
        except Exception:
            logger.exception("分割 bk_token [%s] 失败", bk_token)
            raise ValueError(error_msg)

        if not token_info or len(token_info) < 3:
            raise ValueError(error_msg)

        # 按照加密时的顺序取出
        user_id, expires_at = token_info[1], int(token_info[0])

        return user_id, expires_at


class BkTokenManager:
    def __init__(self):
        # Token 加密密钥
        self.bk_token_processor = BkTokenProcessor()
        # Token 过期间隔
        self.cookie_age = settings.BK_TOKEN_COOKIE_AGE
        # Token 无操作失效间隔
        self.inactive_age = settings.BK_TOKEN_INACTIVE_AGE
        # Token 校验时间允许误差
        self.offset_error_age = settings.BK_TOKEN_OFFSET_ERROR_AGE
        # 无操作失效时间更新间隔（秒）：距离上次更新超过该间隔时才更新 inactive_expires_at，减少数据库写操作
        # 默认值为 600 秒（10 分钟）
        self.inactive_update_interval = settings.BK_TOKEN_INACTIVE_UPDATE_INTERVAL
        # 允许的最大登录终端数量，默认 0 表示不限制
        self.max_sessions = settings.BK_TOKEN_MAX_SESSIONS

        # Token 生成失败的重试次数
        self.allowed_retry_count = 5

    def generate(self, user_id: str) -> Tuple[str, datetime.datetime]:
        """
        生成用户的登录态
        :param user_id: 用户唯一标识符
        :return: bk_token, expires_at
        """
        # 实现登录终端数量限制
        if self.max_sessions > 0:
            # 如果设置了最大会话数限制，则保留最新的 (max_sessions - 1) 个 token，将更旧的 token 标记为失效
            try:
                # 查询该用户所有有效的 token，按 ID 倒序排列（ID 自增，大的更新）
                active_tokens = BkToken.objects.filter(user_id=user_id, is_logout=False).order_by("-id")

                # 如果当前有效 token 数量 >= 最大会话数，需要将最旧的 token 标记为失效
                if active_tokens.count() >= self.max_sessions:
                    # 直接获取需要失效的 token（跳过最新的 max_sessions - 1 个，剩余的都是旧的）
                    tokens_to_invalidate = list(active_tokens[self.max_sessions - 1 :].values_list("id", flat=True))
                    # 将这些旧 token 标记为失效
                    BkToken.objects.filter(id__in=tokens_to_invalidate).update(is_logout=True)
            except Exception:
                logger.exception("标记用户 [%s] 的旧 token 失效时发生错误", user_id)

        bk_token = ""
        expires_at = int(time.time())
        # 重试 5 次
        retry_count = 0
        while not bk_token and retry_count < self.allowed_retry_count:
            now_time = int(time.time())
            # Token 过期时间
            expires_at = now_time + self.cookie_age
            # Token 无操作失效时间
            inactive_expires_at = now_time + self.inactive_age
            # 生成 bk_token
            bk_token = self.bk_token_processor.generate(user_id, expires_at)
            # DB 记录
            try:
                BkToken.objects.create(token=bk_token, user_id=user_id, inactive_expires_at=inactive_expires_at)
            except Exception:
                logger.exception("Login ticket failed to be saved during ticket generation")
                # 循环结束前将 bk_token 置空后重新生成
                bk_token = "" if retry_count + 1 < self.allowed_retry_count else bk_token
            retry_count += 1
        # Note: quote_plus 是为了兼容 2.x 版本，保持一致，避免用于 Cookie 时调用方未进行 url encode
        return quote_plus(bk_token), datetime.datetime.fromtimestamp(expires_at, timezone.get_current_timezone())

    def is_valid(self, bk_token: str) -> Tuple[bool, str, str]:  # noqa: PLR0911
        """
        验证用户登录态
        :return: ok, user_id, msg
        """
        if not bk_token:
            return False, "", _("参数 bk_token 缺失")

        # Note: unquote_plus 是为了兼容 2.x 版本，因为旧版本在设置 bk_token Cookie 时做了 quote_plus 转换编码
        bk_token = unquote_plus(bk_token)
        # 解析 bk_token 获取 user_id 和过期时间
        try:
            user_id, expires_at = self.bk_token_processor.parse(bk_token)
        except ValueError as error:
            return False, "", str(error)

        # 检查 DB 是存在
        try:
            bk_token_obj = BkToken.objects.get(token=bk_token)
            is_logout = bk_token_obj.is_logout
            inactive_expires_at = bk_token_obj.inactive_expires_at
        except Exception:  # noqa: BLE001
            return False, "", _("不存在 bk_token[%s] 的记录").format(bk_token)

        # token 已注销
        if is_logout:
            return False, "", _("登录态已注销")

        now = int(time.time())
        # token 有效期已过
        if now > expires_at + self.offset_error_age:
            return False, "", _("登录态已过期")

        # token 有效期大于当前时间的有效期
        if expires_at - now > self.cookie_age + self.offset_error_age:
            return False, "", _("登录态有效期不合法")

        # token 无操作有效期已过
        if now > inactive_expires_at + self.inactive_age:
            return False, "", _("长时间无操作，登录态已过期")

        # 更新 无操作有效期（仅在距离上次更新超过更新间隔时更新，减少数据库写操作）
        # inactive_expires_at 记录了上次设置的值（上次 now + inactive_age）
        # 计算距离上次更新的时间间隔：now - (inactive_expires_at - inactive_age)
        # 只有当距离上次更新超过更新间隔时才更新
        if now - (inactive_expires_at - self.inactive_age) >= self.inactive_update_interval:
            try:
                BkToken.objects.filter(token=bk_token).update(inactive_expires_at=now + self.inactive_age)
            except Exception:
                logger.exception("update inactive_expires_at fail")

        return True, user_id, ""

    @staticmethod
    def set_invalid(bk_token: str):
        """
        设置登录态失效
        """
        # Note: unquote_plus 是为了兼容 2.x 版本，因为旧版本在设置 bk_token Cookie 时做了 quote_plus 转换编码
        bk_token = unquote_plus(bk_token)
        BkToken.objects.filter(token=bk_token).update(is_logout=True)
