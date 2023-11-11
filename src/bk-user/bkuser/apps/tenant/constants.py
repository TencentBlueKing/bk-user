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
import re

import pytz
from blue_krill.data_types.enum import EnumField, FeatureFlag, FeatureFlagField, StructuredEnum
from django.utils.translation import gettext_lazy as _

TIME_ZONE_CHOICES = [(i, i) for i in list(pytz.common_timezones)]

TENANT_ID_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9-]{2,31}")


class TenantFeatureFlag(FeatureFlag):  # type: ignore
    """租户特性标志"""

    USER_NUMBER_VISIBLE = FeatureFlagField(label=_("人员数量是否可见"), default=True)


class UserFieldDataType(str, StructuredEnum):
    """租户用户自定义字段数据类型"""

    STRING = EnumField("string", label=_("字符串"))
    NUMBER = EnumField("number", label=_("数字"))
    ENUM = EnumField("enum", label=_("枚举"))
    MULTI_ENUM = EnumField("multi_enum", label=_("多选枚举"))


class NotificationMethod(str, StructuredEnum):
    """通知方式"""

    EMAIL = EnumField("email", label=_("邮件通知"))
    SMS = EnumField("sms", label=_("短信通知"))


class NotificationScene(str, StructuredEnum):
    """通知场景"""

    TENANT_USER_EXPIRING = EnumField("tenant_user_expiring", label=_("租户用户即将过期"))
    TENANT_USER_EXPIRED = EnumField("tenant_user_expired", label=_("租户用户已过期"))


DEFAULT_TENANT_USER_VALIDITY_PERIOD_CONFIG = {
    "enabled": True,
    "validity_period": 365,
    "remind_before_expire": [7],
    "enabled_notification_methods": [NotificationMethod.EMAIL],
    "notification_templates": [
        {
            "method": NotificationMethod.EMAIL,
            "scene": NotificationScene.TENANT_USER_EXPIRING,
            "title": "蓝鲸智云 - 账号即将到期提醒!",
            "sender": "蓝鲸智云",
            "content": (
                "{{ username }}, 您好：\n "
                + "您的蓝鲸智云平台账号将于 {{ remind_before_expire_days }} 天后到期。"
                + "为避免影响使用，请尽快联系平台管理员进行续期。\n "
                + "此邮件为系统自动发送，请勿回复。\n "
            ),
            "content_html": (
                "<p>{{ username }}, 您好：</p>"
                + "<p>您的蓝鲸智云平台账号将于 {{ remind_before_expire_days }} 天后到期。"
                + "为避免影响使用，请尽快联系平台管理员进行续期。</p>"
                + "<p>此邮件为系统自动发送，请勿回复。</p>"
            ),
        },
        {
            "method": NotificationMethod.EMAIL,
            "scene": NotificationScene.TENANT_USER_EXPIRED,
            "title": "蓝鲸智云 - 账号到期提醒!",
            "sender": "蓝鲸智云",
            "content": (
                "{{ username }}，您好：\n "
                + "您的蓝鲸智云平台账号已过期。为避免影响使用，请尽快联系平台管理员进行续期。\n "  # noqa: E501
                + "该邮件为系统自动发送，请勿回复。"  # noqa: E501
            ),
            "content_html": (
                "<p>{{ username }}，您好：</p>"
                + "<p>您的蓝鲸智云平台账号已过期，如需继续使用，请尽快联系平台管理员进行续期。</p>"  # noqa: E501
                + "<p>此邮件为系统自动发送，请勿回复。</p>"
            ),
        },
        {
            "method": NotificationMethod.SMS,
            "scene": NotificationScene.TENANT_USER_EXPIRING,
            "title": None,
            "sender": "蓝鲸智云",
            "content": (
                "{{ username }}，您好：\n "
                + "您的蓝鲸智云平台账号将于 {{ remind_before_expire_days }} 天后到期。"
                + "为避免影响使用，请尽快联系平台管理员进行续期。\n "
                + "该短信为系统自动发送，请勿回复。"
            ),
            "content_html": (
                "<p>{{ username }}，您好：</p>"
                + "<p>您的蓝鲸智云平台账号将于 {{ remind_before_expire_days }} 天后到期。"
                + "为避免影响使用，请尽快联系平台管理员进行续期。</p>"
                + "<p>该短信为系统自动发送，请勿回复。</p>"
            ),
        },
        {
            "method": NotificationMethod.SMS,
            "scene": NotificationScene.TENANT_USER_EXPIRED,
            "title": None,
            "sender": "蓝鲸智云",
            "content": (
                "{{ username }}您好：\n "
                + "您的蓝鲸智云平台账号已过期，如需继续使用，请尽快联系平台管理员进行续期。\n "  # noqa: E501
                + "该短信为系统自动发送，请勿回复。"  # noqa: E501
            ),
            "content_html": (
                "<p>{{ username }}您好：</p>"
                + "<p>您的蓝鲸智云平台账号已过期，如需继续使用，请尽快联系平台管理员进行续期。</p>"  # noqa: E501
                + "<p>该短信为系统自动发送，请勿回复。</p>"
            ),
        },
    ],
}
