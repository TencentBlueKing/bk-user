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
from phonenumbers import UNKNOWN_REGION, NumberParseException, region_code_for_country_code

logger = logging.getLogger(__name__)


def validate_phone_with_country_code(phone: str, country_code: str) -> None:
    """校验 phone 与 country_code 是否匹配且合法

    :raise ValueError: country_code 或 phone 不合法
    """
    try:
        region = region_code_for_country_code(int(country_code))
    except Exception:
        raise ValueError(f"parse phone country code [{country_code}] to region failed!")

    # 解析出未知区号
    if region == UNKNOWN_REGION:
        raise ValueError(f"unknown phone country code: {country_code}")

    # 特殊检查：中国手机号强制要求必须是 11 位
    if region == "CN" and len(phone) != 11:  # noqa: PLR2004
        raise ValueError(f"chinese phone number must be 11 digits, {phone} is invalid")

    try:
        phonenumbers.parse(phone, region)
    except NumberParseException:
        raise ValueError(f"parse phone number [{phone}] with country code [{country_code}] region [{region}] failed!")
