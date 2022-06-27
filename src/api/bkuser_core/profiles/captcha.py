# -*- coding: utf-8 -*-
import hashlib
import json
import random
import string

from django.conf import settings
from django.core.cache import caches


class CaptchaOperator:
    def __init__(self):
        self.cache = caches["captcha"]

    def generate_token_of_captcha(self, username: str):
        # APP_Secret 区别环境差异
        hashed_value = f"{username}|{settings.APP_TOKEN}"
        md = hashlib.md5()
        md.update(hashed_value.encode("utf-8"))
        return md.hexdigest()

    def set_captcha(self):
        return "".join(random.sample(string.digits, 8))

    def captcha_is_exist(self, token):
        # 校验是否重复发送
        if self.get_captcha_data(token):
            return True

    def get_captcha_data(self, token):
        return json.loads(self.cache.get(token))

    def set_captcha_data(self, token, data):
        self.cache.set(key=token, timeout=data["expire_seconds"], value=json.dumps(data))

    def delete_captcha(self, token):
        self.cache.delete(key=token)
