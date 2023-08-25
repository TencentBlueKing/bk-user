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

import phonenumbers
from phonenumbers import NumberParseException, region_code_for_country_code

from bkuser.common.constants import CHINESE_PHONE_LENGTH, CHINESE_REGION
from bkuser.common.error_codes import error_codes

logger = logging.getLogger(__name__)


def validate_phone_with_country_code(phone: str, country_code: str):
    try:
        region = region_code_for_country_code(int(country_code))

    except ValueError:
        logger.debug("failed to parse phone_country_code: %s, ", country_code)
        raise error_codes.PHONE_PARSE_ERROR.f("手机地区码 {} 解析异常".format(country_code))

    # phonenumbers库在验证号码的时：过短会解析为有效号码，超过250的字节才算超长
    # =》所以这里需要显式做中国号码的长度校验
    if region == CHINESE_REGION and len(phone) != CHINESE_PHONE_LENGTH:
        raise error_codes.PHONE_PARSE_ERROR.f("手机号 {} 长度异常".format(phone))
    try:
        # 按照指定地区码解析手机号
        phonenumbers.parse(phone, region)

    except NumberParseException:  # pylint: disable=broad-except
        logger.debug("failed to parse phone number: %s", phone)
        raise error_codes.PHONE_PARSE_ERROR.f("手机号 {} 解析异常".format(phone))
