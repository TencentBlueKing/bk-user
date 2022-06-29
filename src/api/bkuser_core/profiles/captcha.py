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
import random
import string

import redis
from django.conf import settings

from bkuser_core.common.error_codes import error_codes
from bkuser_core.profiles.models import Profile


class Captcha:
    def __init__(self):
        self.cache = redis.Redis.from_url(settings.REDIS_URL)

    def _generate_token(self, username: str):
        # APP_Secret 区别环境差异
        hashed_value = f"{username}|{settings.APP_TOKEN}"
        md = hashlib.md5()
        md.update(hashed_value.encode("utf-8"))
        return md.hexdigest()

    def _generate_captcha(self):
        return "".join(random.sample(string.digits, 8))

    def is_username_has_generate_captcha(self, username):
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

    def verify_captcha(self, data):
        captcha_data = Captcha().get_captcha_data(token=data["token"])
        # token 校验
        if not captcha_data:
            raise error_codes.CAPTCHA_TOKEN_EXPIRED
        # 安全校验，token被串改，为其它用户的token
        profile = Profile.objects.get(id=captcha_data["profile"])
        # 用户名
        if profile.username != data["username"]:
            raise error_codes.CAPTCHA_TOKEN_EXPIRED
        # 目录域
        if profile.domain != data["domain"]:
            raise error_codes.DOMAIN_UNKNOWN
        # 验证码
        if captcha_data["captcha"] != data["captcha"]:
            raise error_codes.CAPTCHA_WRONG
        # 验证通过删除缓存
        self.delete_captcha(data["token"])
        return captcha_data

    def generate_captcha(self, data):
        profile = data["profile"]
        captcha_data = {"profile": profile.id, "username": profile.username, "domain": profile.domain}
        token = self._generate_token(f"{profile.username}@{profile.domain}")
        captcha = self._generate_captcha()
        captcha_data.update(
            {
                "send_method": data["send_method"],
                "authenticated_value": data["authenticated_value"],
                "captcha": captcha,
            }
        )
        self.cache.set(name=token, value=json.dumps(captcha_data), ex=data["expire_seconds"])
        return token, captcha_data
