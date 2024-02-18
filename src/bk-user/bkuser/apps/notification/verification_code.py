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
import random
import string
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bkuser.apps.notification.constants import NotificationMethod, VerificationCodeScene
from bkuser.apps.notification.exceptions import (
    ExceedSendVerificationCodeLimit,
    ExceedVerificationCodeRetries,
    InvalidVerificationCode,
)
from bkuser.apps.notification.tasks import send_verification_code_to_user
from bkuser.apps.tenant.models import TenantUser
from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum


class VerificationCodeManager:
    """邮箱 / 手机验证码"""

    # 验证码过期时间
    cache_timeout = settings.VERIFICATION_CODE_VALID_TIME

    def __init__(self, tenant_user: TenantUser, scene: VerificationCodeScene):
        self.tenant_user = tenant_user
        self.scene = scene
        self.cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.VERIFICATION_CODE)
        self.retries_cache_key = self._gen_cache_key("retries")
        self.code_cache_key = self._gen_cache_key("code")
        self.send_cnt_cache_key = self._gen_cache_key("send_cnt")

    def validate(self, code: str):
        """校验验证码是否正确"""
        if not self._can_retries():
            raise ExceedVerificationCodeRetries(_("超过验证码重试次数"))

        if self._get_verification_code() != code:
            raise InvalidVerificationCode(_("验证码错误或已失效"))

        # 校验通过后，需要清理掉验证码避免二次使用
        self.cache.delete(self.code_cache_key)
        self.cache.delete(self.retries_cache_key)

    def send(self, method: NotificationMethod):
        """发送验证码"""
        if not self._can_send():
            raise ExceedSendVerificationCodeLimit(_("超过验证码发送次数限制"))

        send_verification_code_to_user.delay(self.tenant_user.id, method, self._get_verification_code())

    def _can_retries(self) -> bool:
        """检查当前验证码试错次数"""
        retries = self.cache.get(self.retries_cache_key, 0)
        if retries < settings.VERIFICATION_CODE_MAX_RETRIES:
            self.cache.set(self.retries_cache_key, retries + 1, timeout=self.cache_timeout)
            return True

        self.cache.delete(self.code_cache_key)
        self.cache.delete(self.retries_cache_key)
        return False

    def _can_send(self) -> bool:
        """检查当前验证码发送次数"""
        send_cnt = self.cache.get(self.send_cnt_cache_key, 0)
        if send_cnt < settings.VERIFICATION_CODE_MAX_SEND_PER_DAY:
            # 今天结束后过期
            midnight = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            expire_seconds = (midnight - timezone.now()).total_seconds()
            self.cache.set(self.send_cnt_cache_key, send_cnt + 1, timeout=expire_seconds)
            return True

        return False

    def _get_verification_code(self) -> str:
        """从缓存中获取 / 生成验证码"""
        if code := self.cache.get(self.code_cache_key):
            return code

        # 验证码字符集：数字，大小写字母
        code = "".join(random.sample(string.ascii_letters + string.digits, settings.VERIFICATION_CODE_LENGTH))
        # 刷新缓存中的验证码
        self.cache.set(self.code_cache_key, code, timeout=self.cache_timeout)
        # 重置试错次数
        self.cache.delete(self.retries_cache_key)
        return code

    def _gen_cache_key(self, key_type: str) -> str:
        """生成验证码缓存 key"""
        return f"{self.scene.value}:{self.tenant_user.id}:{key_type}"
