# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import secrets
import string

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum
from bkuser.common.verification_code.constants import VerificationCodeScene
from bkuser.common.verification_code.exceptions import GenerateCodeTooFrequently, InvalidVerificationCode


class VerificationCodeManager:
    """手机短信验证码"""

    lock_timeout = 60

    def __init__(self, phone: str, phone_country_code: str, scene: VerificationCodeScene):
        self.phone = phone
        self.phone_country_code = phone_country_code
        self.scene = scene
        self.cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.VERIFICATION_CODE)
        self.retries_cache_key = self._gen_cache_key("retries")
        self.code_cache_key = self._gen_cache_key("code")
        self.lock_cache_key = self._gen_cache_key("lock")

    def validate(self, code: str):
        """校验验证码是否正确"""
        if not self._can_retries():
            raise InvalidVerificationCode(_("超过验证码重试次数"))

        if self.cache.get(self.code_cache_key) != code:
            raise InvalidVerificationCode(_("验证码错误或已失效"))

        # 校验通过后，需要清理掉验证码避免二次使用
        self.cache.delete(self.code_cache_key)
        self.cache.delete(self.retries_cache_key)

    def _can_retries(self) -> bool:
        """检查当前验证码试错次数"""
        retries = self.cache.get(self.retries_cache_key, 0)
        if retries < settings.VERIFICATION_CODE_MAX_RETRIES:
            self.cache.set(self.retries_cache_key, retries + 1, timeout=settings.VERIFICATION_CODE_VALID_TIME)
            return True

        self.cache.delete(self.code_cache_key)
        return False

    def gen_code(self) -> str:
        # 生成验证码有频率限制，不能短时间内频繁生成
        if self.cache.get(self.lock_cache_key):
            raise GenerateCodeTooFrequently(_("生成验证码过于频繁，请稍后再试"))

        self.cache.set(self.lock_cache_key, True, timeout=self.lock_timeout)

        # 验证码字符集：数字，大小写字母
        charset = string.ascii_letters + string.digits
        code = "".join(secrets.choice(charset) for _ in range(settings.VERIFICATION_CODE_LENGTH))
        # 刷新缓存中的验证码
        self.cache.set(self.code_cache_key, code, timeout=settings.VERIFICATION_CODE_VALID_TIME)
        # 重置试错次数
        self.cache.delete(self.retries_cache_key)
        return code

    def _gen_cache_key(self, key_type: str) -> str:
        """生成验证码缓存 key"""
        return f"{self.scene.value}:{self.phone_country_code}:{self.phone}:{key_type}"
