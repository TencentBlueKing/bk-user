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

from bkuser_core.api.web.constants import ONE_MINUTE_OF_SECONDS
from bkuser_core.api.web.password.tasks import send_reset_password_verification_code_sms
from bkuser_core.common.error_codes import error_codes
from bkuser_core.profiles.models import Profile, ProfileTokenHolder
from bkuser_core.user_settings.loader import ConfigProvider

logger = logging.getLogger(__name__)


class VerificationCodeBaseHandler:
    def __init__(self, profile):

        self.profile = profile
        if self.profile:
            self.config_loader = ConfigProvider(category_id=profile.category_id)
        self.cache = caches["verification_code"]

    def _generate_token(self) -> str:
        hashed_value = f"{self.profile.username}@{self.profile.domain}|{self.profile.telephone}"
        md = hashlib.md5()
        md.update(hashed_value.encode("utf-8"))
        return md.hexdigest()

    def _set_data(self, key: str, data: Any, timeout: int = None, prefix: str = None):
        if prefix:
            key = f"{prefix}_{key}"
        if timeout:
            self.cache.set(key=key, timeout=timeout, value=data)
        else:
            self.cache.set(key=key, value=data)

    def _get_data(self, key: str, prefix: str = None):
        if prefix:
            key = f"{prefix}_{key}"
        data = self.cache.get(key=key)
        return data

    def _delete(self, key: str, prefix: str = None):
        if prefix:
            key = f"{prefix}_{key}"
        self.cache.delete(key=key)

    def _generate_ramdom_verification_code(self, code_length: int) -> str:
        return "".join(random.sample(string.digits, code_length))


class ResetPasswordVerificationCodeHandler(VerificationCodeBaseHandler):
    def get_reset_password_data(self, token: str) -> dict:
        data = self._get_data(token, prefix="reset_password")
        return json.loads(data) if data else {}

    def set_reset_password_data(self, token, data, expire_seconds):
        return self._set_data(token, data, expire_seconds, prefix="reset_password")

    def delete_reset_password_data(self, token):
        return self._delete(token, prefix="reset_password")

    def is_profile_had_generated_verification_code(self, token: str) -> bool:
        # 校验是否重复发送
        if self.get_reset_password_data(token):
            return True
        return False

    def get_reset_password_send_count(self, telephone: str) -> int:
        data = self._get_data(key=telephone, prefix="reset_password_send_count_")
        return int(data) if data else 0

    def set_reset_password_send_count(self, telephone: str, count: int):
        # 当天23：59：59失效
        current_datetime = now()
        today_last_time = datetime.datetime(
            year=current_datetime.year,
            month=current_datetime.month,
            day=current_datetime.day,
            hour=23,
            minute=59,
            second=59,
        )
        #  再次发送的情况下 ++ 1 会重置时间; 计算当前时间距离凌晨时间
        expired_second = today_last_time.timestamp() - current_datetime.timestamp()
        return self._set_data(telephone, count, timeout=expired_second, prefix="reset_password_send_count_")

    def validate_before_generate(self, token: str):

        # 校验是否重复发送
        if self.is_profile_had_generated_verification_code(token):
            effective_minutes = self.config_loader.get("verification_code_expire_seconds")
            raise error_codes.VERIFICATION_CODE_HAD_SEND.f(
                effective_minutes=effective_minutes // ONE_MINUTE_OF_SECONDS
            )

        # 是否在发送的当日次数中
        limit_count = self.config_loader.get("reset_sms_send_max_limit")
        reset_password_send_count = self.get_reset_password_send_count(self.profile.telephone)
        if reset_password_send_count > limit_count:
            raise error_codes.VERIFICATION_CODE_SEND_LIMIT

    def generate_reset_password_token(self) -> str:
        # token 生成
        token = self._generate_token()
        # 是否已经发送，是否超过当日发送次数
        self.validate_before_generate(token)

        expire_seconds = self.config_loader.get("verification_code_expire_seconds")
        verification_code_length = self.config_loader.get("verification_code_length")
        # 生成验证码
        verification_code = self._generate_ramdom_verification_code(verification_code_length)
        expired_at = now() + datetime.timedelta(seconds=expire_seconds)
        verification_code_data = {
            "profile_id": self.profile.id,
            "verification_code": verification_code,
            "error_count": 0,
            # 设置过期点的时间戳，正常情况下会自动过期，但是输入错误的情况下 error_count ++ 1 会重置时间
            "expired_at_timestamp": expired_at.timestamp(),
        }

        logger.info("Set the captcha_data in redis. token: {}".format(token))
        # redis 缓冲验证码
        self.set_reset_password_data(token, json.dumps(verification_code_data), expire_seconds)

        # 增加当日发送次数
        send_count = self.get_reset_password_send_count(self.profile.telephone) + 1
        self.set_reset_password_send_count(self.profile.telephone, send_count)

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

    def verify_verification_code(self, input_token: str, input_verification_code: str):
        verification_code_data = self.get_reset_password_data(token=input_token)

        # token 校验
        if not verification_code_data:
            logger.info(
                "verify captcha, verification_code_data is invalid. Posted token is %s, captcha=%s",
                input_token,
                input_verification_code,
            )
            raise error_codes.VERIFICATION_CODE_INVALID

        logger.info(
            "verify captcha, verification_code_data is %s. Posted token is %s, captcha=%s",
            verification_code_data,
            input_token,
            input_verification_code,
        )

        self.profile = Profile.objects.get(id=verification_code_data["profile_id"])
        self.config_loader = ConfigProvider(category_id=self.profile.category_id)

        # 验证码校验
        if verification_code_data["verification_code"] != input_verification_code:
            verification_code_data["error_count"] += 1
            expired_second = verification_code_data["expired_at_timestamp"] - now().timestamp()
            # 输入错误，刚好临近过期
            if expired_second < 0:
                raise error_codes.VERIFICATION_CODE_INVALID
            self.set_reset_password_data(
                input_token, json.dumps(verification_code_data), expire_seconds=expired_second
            )
            error_count_limit = self.config_loader.get("failed_verification_max_limit")
            # 验证码试错次数
            if verification_code_data["error_count"] > error_count_limit:
                raise error_codes.VERIFICATION_CODE_FAILED_MAX_COUNT
            # 验证码错误
            raise error_codes.VERIFICATION_CODE_FAILED
        # 验证通过删除缓存
        self.delete_reset_password_data(input_token)

    def generate_profile_token(self) -> ProfileTokenHolder:
        token_holder = ProfileTokenHolder.objects.create(profile=self.profile)
        return token_holder
