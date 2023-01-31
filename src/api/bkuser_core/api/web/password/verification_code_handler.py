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
import hashlib
import json
import logging
import random
import string
from typing import Any

from django.core.cache import caches
from django.utils.timezone import now

from bkuser_core.api.web.password.tasks import send_reset_password_verification_code_sms
from bkuser_core.common.error_codes import error_codes
from bkuser_core.profiles.models import Profile, ProfileTokenHolder
from bkuser_core.user_settings.loader import ConfigProvider

logger = logging.getLogger(__name__)


class ResetPasswordVerificationCodeHandler:
    def __init__(self):
        self.profile = None
        self.config_loader = None
        self.cache = caches["verification_code"]

    def _set_into_cache(self, key: str, data: Any, timeout: int, prefix: str = None):
        if prefix:
            key = f"{prefix}_{key}"
        self.cache.set(key=key, timeout=timeout, value=data)

    def _get_from_cache(self, key: str, prefix: str = None):
        if prefix:
            key = f"{prefix}_{key}"
        data = self.cache.get(key=key)
        return data

    def _delete_from_cache(self, key: str, prefix: str = None):
        if prefix:
            key = f"{prefix}_{key}"
        self.cache.delete(key=key)

    def _set_reset_password_send_count(self, telephone: str, count: int):
        # 当天23：59：59失效
        current_datetime = now()
        today_last_time = datetime.datetime(
            year=current_datetime.year,
            month=current_datetime.month,
            day=current_datetime.day,
            hour=23,
            minute=59,
            second=59,
            tzinfo=current_datetime.tzinfo,
        )
        #  再次发送的情况下 ++ 1 会重置时间; 计算当前时间距离凌晨时间
        expired_second = today_last_time.timestamp() - current_datetime.timestamp()
        return self._set_into_cache(telephone, count, timeout=expired_second, prefix="reset_password_send_count")

    def _check_repeat_send_require(self, token: str):
        # 校验是否重复发送
        verification_code_data = self._get_from_cache(token, prefix="reset_password")
        if verification_code_data:
            effective_minutes = self.config_loader.get("verification_code_expire_seconds")
            raise error_codes.VERIFICATION_CODE_REPEAT_SENDING_REQUIRE.f(effective_minutes=effective_minutes // 60)

    def _check_send_count_exceeded_limit(self):
        # 是否在发送的当日次数中
        limit_send_count = self.config_loader.get("reset_sms_send_max_limit")
        send_count_in_cache = self._get_from_cache(key=self.profile.telephone, prefix="reset_password_send_count")
        send_count = send_count_in_cache if send_count_in_cache else 0
        if send_count > limit_send_count:
            raise error_codes.VERIFICATION_CODE_SEND_REACH_LIMIT

    def generate_reset_password_token(self, profile_id) -> str:
        self.profile = Profile.objects.get(id=profile_id)
        self.config_loader = ConfigProvider(category_id=self.profile.category_id)

        # token 生成
        hashed_value = f"{self.profile.username}@{self.profile.domain}|{self.profile.telephone}"
        md = hashlib.md5()
        md.update(hashed_value.encode("utf-8"))
        token = md.hexdigest()

        # 是否已经发送，是否超过当日发送次数
        self._check_repeat_send_require(token)
        self._check_send_count_exceeded_limit()

        expire_seconds = self.config_loader.get("verification_code_expire_seconds")
        verification_code_length = self.config_loader.get("verification_code_length")

        # 生成验证码
        verification_code = "".join(random.sample(string.digits, verification_code_length))
        expired_at = now() + datetime.timedelta(seconds=expire_seconds)
        verification_code_data = {
            "profile_id": self.profile.id,
            "verification_code": verification_code,
            "error_count": 0,
            # 设置过期点的时间戳，正常情况下会自动过期，但是输入错误的情况下 error_count ++ 1 会重置时间
            "expired_at_timestamp": expired_at.timestamp(),
        }

        logger.info(
            "Set the verification_code_data in redis. profile<%s-%s>  token: %s",
            self.profile.id,
            f"{self.profile.username}@{self.profile.domain}",
            token,
        )
        # redis 缓存验证码
        self._set_into_cache(token, json.dumps(verification_code_data), expire_seconds, prefix="reset_password")

        # 增加当日发送次数
        send_count_in_cache = self._get_from_cache(key=self.profile.telephone, prefix="reset_password_send_count")
        send_count = send_count_in_cache + 1 if send_count_in_cache else 1
        self._set_reset_password_send_count(self.profile.telephone, send_count)

        reset_password_sms_config = self.config_loader.get("reset_password_sms_config")

        sms_message_send_config = {
            "sender": reset_password_sms_config["sender"],
            "message": reset_password_sms_config["content"].format(verification_code=verification_code),
            "receivers": [self.profile.telephone],
        }

        send_reset_password_verification_code_sms.delay(
            profile_id=self.profile.id, send_config=sms_message_send_config
        )

        return token

    def verify_verification_code(self, verification_code_token: str, verification_code: str) -> int:
        verification_code_data_bytes = self._get_from_cache(verification_code_token, prefix="reset_password")

        # token 校验
        if not verification_code_data_bytes:
            logger.info(
                "verify verification_code, verification_code_data is invalid. Posted token is %s",
                verification_code_token,
            )
            raise error_codes.VERIFICATION_CODE_INVALID

        verification_code_data = json.loads(verification_code_data_bytes)
        logger.info(
            "verify verification_code. Posted token is %s, verification_code=%s",
            verification_code_token,
            verification_code,
        )

        profile = Profile.objects.get(id=verification_code_data["profile_id"])
        config_loader = ConfigProvider(profile.category_id)

        # 验证码校验
        if verification_code_data["verification_code"] != verification_code:
            verification_code_data["error_count"] += 1
            expired_second = verification_code_data["expired_at_timestamp"] - now().timestamp()
            # 输入错误，刚好临近过期
            if expired_second < 0:
                raise error_codes.VERIFICATION_CODE_INVALID

            self._set_into_cache(
                verification_code_token, json.dumps(verification_code_data), expired_second, prefix="reset_password"
            )
            error_count_limit = config_loader.get("failed_verification_max_limit")

            # 验证码试错次数
            if verification_code_data["error_count"] > error_count_limit:
                raise error_codes.VERIFICATION_CODE_WRONG_REACH_LIMIT

            # 验证码错误
            raise error_codes.VERIFICATION_CODE_WRONG

        # 验证通过删除缓存
        self._delete_from_cache(verification_code_token, prefix="reset_password")
        return profile.id

    def generate_profile_token(self, profile_id) -> ProfileTokenHolder:
        profile = Profile.objects.get(id=profile_id)
        token_holder = ProfileTokenHolder.objects.create(profile=profile)
        return token_holder
