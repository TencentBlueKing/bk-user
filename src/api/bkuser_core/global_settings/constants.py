# -*- coding: utf-8 -*-
from enum import auto

from bkuser_core.common.enum import AutoLowerEnum

VERIFICATION_TYPE_META = {
    'key': 'verification_type',
    'example': 'two_factor',
    'default': 'two_factor',
    'choices': ["not", "two_factor"],
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
TWO_FACTOR_VERIFICATION_META = [
    {'key': 'send_method', 'example': 'email', 'default': 'email', 'choices': ['email', 'telephone']},
    {'key': 'verification_enable', 'example': False, 'default': False, 'choices': [False, True]},
    {'key': 'expire_seconds', 'example': 300, 'default': 300},
    {
        'key': 'scope',
        'example': {'categories': [], 'departments': [], 'profiles': []},
        'default': {'categories': [], 'departments': [], 'profiles': []},
    },
    {'key': 'expire_seconds', 'example': 300, 'default': 300},
    {'key': 'email_config', 'example': email_config, 'default': email_config},
    {'key': 'sms_config', 'example': sms_config, 'default': sms_config},
]


class GlobalSettingsEnableNamespaces(AutoLowerEnum):
    GENERAL = auto()
    TWO_FACTOR = auto()

    _choices_labels = (
        (GENERAL, "通用"),
        (TWO_FACTOR, "双因子认证"),
    )
