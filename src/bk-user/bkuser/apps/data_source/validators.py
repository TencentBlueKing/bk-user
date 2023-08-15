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
import logging
import re

import phonenumbers
from django.utils.translation import gettext_lazy as _
from phonenumbers import region_code_for_country_code
from rest_framework.exceptions import ValidationError

USERNAME_REGEX = r"^(\d|[a-zA-Z])([a-zA-Z0-9._-]){0,31}"
logger = logging.getLogger(__name__)
CHINESE_REGION = "CN"
CHINESE_PHONE_LENGTH = 11


def validate_username(value):
    if not re.fullmatch(re.compile(USERNAME_REGEX), value):
        raise ValidationError(_("{} 不符合 username 命名规范").format(value))


def validate_phone(phone_country_code: str, phone: str):
    try:
        # 根据国家码获取对应地区码
        region = region_code_for_country_code(int(phone_country_code))

    except phonenumbers.NumberParseException:
        logger.debug("failed to parse phone_country_code: %s, ", phone_country_code)

    else:
        # phonenumbers库在验证号码的时：过短会解析为有效号码，超过250的字节才算超长
        # =》所以这里需要显式做中国号码的长度校验
        if region == CHINESE_REGION and len(phone) != CHINESE_PHONE_LENGTH:
            raise ValidationError(_("{} 不符合 长度要求").format(phone))

        try:
            # 按照指定地区码解析手机号
            phonenumbers.parse(phone, region)

        except Exception:  # pylint: disable=broad-except
            logger.debug("failed to parse phone number: %s", phone)
            raise ValidationError
