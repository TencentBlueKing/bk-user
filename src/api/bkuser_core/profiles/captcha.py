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

import hashlib
import json
import logging
import random
import string

from django.conf import settings
from django_redis import get_redis_connection

from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.error_codes import error_codes
from bkuser_core.global_settings.constants import GlobalSettingsEnableNamespaces
from bkuser_core.profiles.models import Profile
from bkuser_core.user_settings.loader import GlobalConfigProvider

logger = logging.getLogger(__name__)


class Captcha:
    def __init__(self):
        self.cache = get_redis_connection("captcha")

    def _generate_token(self, username: str):
        # APP_Secret 区别环境差异
        hashed_value = f"{username}|{settings.APP_TOKEN}"
        md = hashlib.md5()
        md.update(hashed_value.encode("utf-8"))
        return md.hexdigest()

    def _generate_captcha(self):
        return "".join(random.sample(string.digits, 8))

    def is_username_has_generated_captcha(self, username):
        # 校验是否重复发送
        token = self._generate_token(username)
        if self.get_captcha_data(token):
            return True
        return False

    def get_captcha_data(self, token):
        data = self.cache.get(name=token)
        return json.loads(data) if data else None

    def set_captcha_data(self, token, data):
        self.cache.set(name=token, ex=data["expire_seconds"], value=json.dumps(data))

    def delete_captcha(self, token):
        self.cache.delete(token)

    def validate_before_generate_captcha(self, authentication_type, data):
        validated_data = {}
        # 根据域，判定用户
        if not data.get("domain"):
            category = ProfileCategory.objects.get_default()
        else:
            try:
                category = ProfileCategory.objects.get(domain=data["domain"])
            except ProfileCategory.DoesNotExist:
                raise error_codes.DOMAIN_UNKNOWN

        username = data.get("username")
        profile = Profile.objects.get(username=username, domain=category.domain)
        validated_data.setdefault("profile", profile)

        authentication_settings = GlobalConfigProvider(authentication_type)

        if authentication_type != GlobalSettingsEnableNamespaces.TWO_FACTOR_AUTHENTICATION.value:
            logger.info(f"Current authentication type is {authentication_type}")
            return None

        # 校验是否重复发送
        if self.is_username_has_generated_captcha(f"{username}@{category.domain}"):
            raise error_codes.CAPTCHA_DUPLICATE_SENDING.f(
                expire_time=int(authentication_settings.get("expire_seconds") / 60)
            )
        validated_data.setdefault("send_method", authentication_settings.get("send_method"))

        # 已绑定，data["authenticated_value"] 有值
        authenticated_value = getattr(profile, authentication_settings.get("send_method"))

        if not authenticated_value:
            # 未绑定，data["authenticated_value"] 为空字符串
            try:
                validated_data["authenticated_value"] = data[authentication_settings.get("send_method")]
            except KeyError:
                raise error_codes.USER_NOT_BIND_EMAIL_TELEPHONE.f(
                    send_method=authentication_settings.get("send_method")
                )
        validated_data["authenticated_value"] = authenticated_value
        validated_data["expire_seconds"] = authentication_settings.get("expire_seconds")
        return validated_data

    def verify_captcha(self, data):
        captcha_data = Captcha().get_captcha_data(token=data["token"])
        logger.info(f"verify captcha, captcha_data is {captcha_data}. Posted data is {data}")

        # token 校验
        if not captcha_data:
            raise error_codes.CAPTCHA_TOKEN_EXPIRED

        username = "{}@{}".format(data["username"], data["domain"])
        if self._generate_token(username=username) != data["token"]:
            raise error_codes.CAPTCHA_TOKEN_EXPIRED

        # 验证码
        if captcha_data["captcha"] != data["captcha"]:
            raise error_codes.CAPTCHA_WRONG

        # 验证通过删除缓存
        self.delete_captcha(data["token"])
        logger.info("Clean the captcha_data in redis , token: {}".format(data["token"]))

        return captcha_data

    def generate_captcha(self, data):
        profile = data["profile"]
        username = f"{profile.username}@{profile.domain}"
        captcha_data = {"profile": profile.id, "username": username}
        token = self._generate_token(username)
        captcha = self._generate_captcha()
        captcha_data.update(
            {
                "send_method": data["send_method"],
                "authenticated_value": data["authenticated_value"],
                "captcha": captcha,
            }
        )
        logger.info("Clean the captcha_data in redis. token: {}".format(data["token"]))
        self.cache.set(token, json.dumps(captcha_data), data["expire_seconds"])
        return token, captcha
