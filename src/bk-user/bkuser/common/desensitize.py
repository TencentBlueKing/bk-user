# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
import re

import phonenumbers

PLACEHOLDER = "--"

# 邮箱
EMAIL_REGEX_PATTERN = re.compile(r"[^@]+@[^@]+\.[^@]+")
# 中国大陆手机号
MAINLAND_PHONE_PATTERN = re.compile(r"^(?:\+?86)?(1\d{10})$")
# 香港手机号
HK_PHONE_PATTERN = re.compile(r"^(?:\+?852)(\d{8})$")
# 澳门手机号
MACAO_PHONE_PATTERN = re.compile(r"^(?:\+?853)(\d{8})$")
# 台湾手机号
TW_PHONE_PATTERN = re.compile(r"^(?:\+?886)(9\d{8})$")
# 海外手机号
OVERSEAS_PHONE_PATTERN = re.compile(r"^(\+\d{1,3})(\d{4,})$")
# 大陆固定电话
MAINLAND_LANDLINE_PATTERN = re.compile(r"^(\d{3,4}-)(\d{7,8})$")


def desensitize_email(email: str) -> str:
    """对邮箱进行脱敏"""
    if not email:
        return PLACEHOLDER

    # 邮箱格式非法，直接返回
    if not re.match(EMAIL_REGEX_PATTERN, email):
        return email

    # 显示 username 前 2 位字符以及 @ 及 @ 后所有字符
    username, domain = email.split("@")
    return username[:2] + "****@" + domain


def desensitize_phone(phone: str) -> str:
    """对手机号进行脱敏"""
    if not phone:
        return "--"

    # 删除空格
    phone = phone.replace(" ", "")

    # 大陆手机：展示前 3 后 4，中间用 4 个 * 代替
    if MAINLAND_PHONE_PATTERN.match(phone):
        phone = re.sub(MAINLAND_PHONE_PATTERN, r"\1", phone)
        return phone[:3] + "****" + phone[7:]

    # 香港、澳门：展示前 2 后 2，中间用 4 个 * 代替
    if HK_PHONE_PATTERN.match(phone):
        phone = re.sub(HK_PHONE_PATTERN, r"\1", phone)
        return phone[:2] + "****" + phone[-2:]

    if MACAO_PHONE_PATTERN.match(phone):
        phone = re.sub(MACAO_PHONE_PATTERN, r"\1", phone)
        return phone[:2] + "****" + phone[-2:]

    # 台湾：展示前 2 后 3，中间用 4 个 * 代替
    if TW_PHONE_PATTERN.match(phone):
        phone = re.sub(TW_PHONE_PATTERN, r"\1", phone)
        return phone[:2] + "****" + phone[-3:]

    # 海外：只展示地区号和中间 4 位，占位符用 4 个 *
    if OVERSEAS_PHONE_PATTERN.match(phone):
        try:
            ret = phonenumbers.parse(phone)
        except phonenumbers.NumberParseException:
            return phone[:2] + "****" + phone[-2:]

        phone, country_code = str(ret.national_number), str(ret.country_code)
        return "+" + country_code + "****" + phone[-8:-4] + "****"

    # 固定电话：只展示区号和后 4 位，中间用 4 个 * 代替
    if MAINLAND_LANDLINE_PATTERN.match(phone):
        area_code, local_number = re.sub(MAINLAND_LANDLINE_PATTERN, r"\1 \2", phone).split()
        return area_code + "****" + local_number[-4:]

    # 没匹配到的展示前 2 后 2，中间 4 个 * 代替
    return phone[:2] + "****" + phone[-2:]
