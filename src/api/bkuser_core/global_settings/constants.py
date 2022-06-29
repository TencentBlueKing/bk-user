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

from enum import auto

from bkuser_core.common.enum import AutoLowerEnum

AUTHENTICATION_TYPE_META = {
    'key': 'authentication_type',
    'example': 'two_factor_authentication',
    'default': 'two_factor_authentication',
    'choices': ["no_authentication", "two_factor_authentication"],
}

email_config = {
    "title": "鲸智云-登录申请",
    "sender": "蓝鲸智云",
    "content": "您正在申请登录平台 " "验证码为：{captcha}" "为保证您账号的安全性，该验证码有效期为{expire_seconds}分钟。如非本人操作，请忽略此邮件",
}
sms_config = {
    "sender": "蓝鲸智云",
    "content": "【蓝鲸智云】您的验证码为{captcha}，请在{expire_seconds}分钟内输入验证码。如非本人操作请忽略",
    "content_html": '<p>【蓝鲸智云】您的验证码为{captcha}，请在{expire_seconds}分钟内输入验证码。如非本人操作请忽略</p>',
}
TWO_FACTOR_AUTHENTICATION_META = [
    {'key': 'send_method', 'example': 'email', 'default': 'email', 'choices': ['email', 'telephone']},
    {'key': 'authentication_enabled', 'example': False, 'default': False, 'choices': [False, True]},
    {'key': 'expire_seconds', 'example': 300, 'default': 300},
    {
        'key': 'scope',
        'example': {'categories': [], 'departments': [], 'profiles': []},
        'default': {'categories': [], 'departments': [], 'profiles': []},
    },
    {'key': 'email_config', 'example': email_config, 'default': email_config},
    {'key': 'sms_config', 'example': sms_config, 'default': sms_config},
]


class GlobalSettingsEnableNamespaces(AutoLowerEnum):
    GENERAL = auto()
    TWO_FACTOR_AUTHENTICATION = auto()

    _choices_labels = (
        (GENERAL, "通用"),
        (TWO_FACTOR_AUTHENTICATION, "双因子认证"),
    )
