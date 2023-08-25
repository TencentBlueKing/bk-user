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

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from bkuser.common.passwd.exceptions import PasswordGenerateError
from bkuser.common.passwd.models import PasswordRule, ValidateResult
from bkuser.common.passwd.validator import PasswordValidator


class PasswordGenerator:
    """密码生成器"""

    def __init__(self, rule: PasswordRule):
        self.rule = rule
        self.charsets = self._gen_charsets()
        self.validator = PasswordValidator(rule)

    def generate(self) -> str:
        """生成密码"""
        for __ in range(settings.GENERATE_RANDOM_PASSWORD_MAX_RETRIES):
            password = self._gen_random_password()
            if self._validate(password).ok:
                return password

        raise PasswordGenerateError(_("无法在有限次数内生成符合预设规则的随机密码，请调整规则"))

    def _gen_charsets(self) -> str:
        """根据指定的规则，生成可选字符集"""
        charsets = ""
        if self.rule.contain_lowercase:
            charsets += string.ascii_lowercase

        if self.rule.contain_uppercase:
            charsets += string.ascii_uppercase

        if self.rule.contain_digit:
            charsets += string.digits

        if self.rule.contain_punctuation:
            charsets += string.punctuation

        return charsets

    def _gen_random_password(self) -> str:
        """根据字符集 + 密码长度范围，生成随机密码"""
        length = random.randint(self.rule.min_length, self.rule.max_length)
        return "".join([random.choice(self.charsets) for _ in range(length)])

    def _validate(self, password: str) -> ValidateResult:
        return self.validator.validate(password)
