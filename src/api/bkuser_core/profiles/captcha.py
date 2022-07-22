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
from django.core.cache import caches

from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.error_codes import error_codes
from bkuser_core.global_settings.constants import GlobalSettingsEnableNamespaces
from bkuser_core.profiles.constants import CAPTCHA_LENGTH
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.tasks import send_captcha
from bkuser_core.profiles.utils import parse_username_domain
from bkuser_core.user_settings.loader import GlobalConfigProvider

logger = logging.getLogger(__name__)


class Captcha:
    def __init__(self):
        self.cache = caches["captcha"]

    def _generate_token(self, username: str):
        # APP_Secret 区别环境差异
        hashed_value = f"{username}|{settings.APP_TOKEN}"
        md = hashlib.md5()
        md.update(hashed_value.encode("utf-8"))
        return md.hexdigest()

    def _generate_ramdom_num(self):
        return "".join(random.sample(string.digits, CAPTCHA_LENGTH))

    def _get_profile(self, username):
        username, domain = parse_username_domain(username)
        try:
            if not domain:
                domain = ProfileCategory.objects.get(default=True).domain
            profile = Profile.objects.get(username=username, domain=domain)
        except Profile.DoesNotExist:
            logger.error("Can`t find the profile: username={}".format(username))
            raise error_codes.USER_DOES_NOT_EXIST
        return profile

    def is_username_has_generated_captcha(self, username):
        # 校验是否重复发送
        token = self._generate_token(username)
        if self.get_data(token):
            return True
        return False

    def get_data(self, token):
        data = self.cache.get(key=token)
        return json.loads(data) if data else None

    def set_data(self, token, data, timeout):
        self.cache.set(key=token, timeout=timeout, value=data)

    def delete(self, token):
        self.cache.delete(key=token)

    def generate_config(self, username, authentication_type, **kwargs):
        captcha_config = {}
        profile = self._get_profile(username)

        authentication_settings = GlobalConfigProvider(authentication_type)
        send_method = authentication_settings.get("send_method")
        contact_detail = getattr(profile, send_method)
        if not contact_detail:
            # 未绑定，data["authenticated_value"] 为空字符串
            contact_detail = kwargs[send_method]

        captcha_config["username"] = username
        captcha_config["profile"] = profile.id
        captcha_config["send_method"] = authentication_settings.get("send_method")
        captcha_config["contact_detail"] = contact_detail
        captcha_config["expire_seconds"] = authentication_settings.get("expire_seconds")
        return captcha_config

    def validate_before_generate(self, username, authentication_type, **kwargs):
        profile = self._get_profile(username)

        authentication_settings = GlobalConfigProvider(authentication_type)

        if authentication_type != GlobalSettingsEnableNamespaces.TWO_FACTOR_AUTHENTICATION.value:
            logger.info(f"Current authentication type is {authentication_type}")
            raise error_codes.NOT_TWO_FACTOR_AUTHENTICATION

        # 校验是否重复发送
        if self.is_username_has_generated_captcha(username):
            raise error_codes.CAPTCHA_DUPLICATE_SENDING.f(
                expire_time=int(authentication_settings.get("expire_seconds") / 60)
            )

        # 已绑定，data["authenticated_value"] 有值
        send_method = authentication_settings.get("send_method")
        authenticated_value = getattr(profile, send_method)
        contact_detail = kwargs.get(send_method)
        if not authenticated_value and not contact_detail:
            raise error_codes.USER_NOT_BIND_CONTACT_DETAILS.f(send_method=send_method)

    def verify_and_get_contact_detail(self, username, token, captcha):
        captcha_data = self.get_data(token=token)

        logger.info(f"verify captcha, captcha_data is {captcha_data}. Posted token is {token}, captcha={captcha}")

        # token 校验
        if not captcha_data:
            raise error_codes.CAPTCHA_TOKEN_EXPIRED

        if self._generate_token(username=username) != token:
            raise error_codes.TOKEN_INVALID

        # 验证码
        if captcha_data["captcha"] != captcha:
            raise error_codes.CAPTCHA_WRONG

        # 验证通过删除缓存
        self.delete(token)
        logger.info("Clean the captcha_data in redis , token: {}".format(token))

    def generate(self, username, authentication_type, **kwargs):
        self.validate_before_generate(username=username, authentication_type=authentication_type, **kwargs)
        config = self.generate_config(username=username, authentication_type=authentication_type, **kwargs)

        profile = config["profile"]
        captcha_data = {"profile": profile, "username": username}
        token = self._generate_token(username)
        captcha = self._generate_ramdom_num()
        captcha_data.update(
            {
                "send_method": config["send_method"],
                "contact_detail": config["contact_detail"],
                "captcha": captcha,
            }
        )
        logger.info("Set the captcha_data in redis. token: {}".format(token))
        self.set_data(token, json.dumps(captcha_data), timeout=config["expire_seconds"])
        send_config = {
            "send_method": config["send_method"],
            "contact_detail": config["contact_detail"],
            "expire_seconds": config["expire_seconds"],
            "profile": profile,
            "captcha": captcha,
        }
        send_captcha.delay(authentication_type=authentication_type, send_config=send_config)

        return token
