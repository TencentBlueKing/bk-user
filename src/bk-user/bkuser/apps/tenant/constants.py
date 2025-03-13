# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
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
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
import re

from blue_krill.data_types.enum import EnumField, StrStructuredEnum
from django.utils.translation import gettext_lazy as _

TENANT_ID_REGEX = re.compile(r"^[a-z][a-z0-9-]{1,30}[a-z0-9]$")

# 自定义字段英文标识命名规则
TENANT_USER_CUSTOM_FIELD_NAME_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{1,30}[a-zA-Z0-9]$")


class BuiltInTenantIDEnum(StrStructuredEnum):
    """内置租户 ID 枚举"""

    DEFAULT = EnumField("default", label="Default")
    SYSTEM = EnumField("system", label="BleuKing Op")


class UserFieldDataType(StrStructuredEnum):
    """租户用户自定义字段数据类型"""

    STRING = EnumField("string", label=_("字符串"))
    NUMBER = EnumField("number", label=_("数字"))
    ENUM = EnumField("enum", label=_("枚举"))
    MULTI_ENUM = EnumField("multi_enum", label=_("多选枚举"))


class NotificationMethod(StrStructuredEnum):
    """通知方式"""

    EMAIL = EnumField("email", label=_("邮件通知"))
    SMS = EnumField("sms", label=_("短信通知"))


class NotificationScene(StrStructuredEnum):
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
            "title": "蓝鲸智云 - 账号即将到期提醒！",
            "sender": "蓝鲸智云",
            "content": (
                "{{ username }}, 您好：\n "
                + "您的蓝鲸智云平台账号将于 {{ valid_days }} 天后到期。"
                + "为避免影响使用，请尽快联系平台管理员进行续期。\n "
                + "此邮件为系统自动发送，请勿回复。\n "
            ),
            "content_html": (
                "<p>{{ username }}, 您好：</p>"
                + "<p>您的蓝鲸智云平台账号将于 {{ valid_days }} 天后到期。"
                + "为避免影响使用，请尽快联系平台管理员进行续期。</p>"
                + "<p>此邮件为系统自动发送，请勿回复。</p>"
            ),
        },
        {
            "method": NotificationMethod.EMAIL,
            "scene": NotificationScene.TENANT_USER_EXPIRED,
            "title": "蓝鲸智云 - 账号到期提醒！",
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


class TenantStatus(StrStructuredEnum):
    """租户状态"""

    ENABLED = EnumField("enabled", label=_("启用"))
    DISABLED = EnumField("disabled", label=_("禁用"))


class TenantUserStatus(StrStructuredEnum):
    """租户用户状态"""

    ENABLED = EnumField("enabled", label=_("启用"))
    DISABLED = EnumField("disabled", label=_("禁用"))
    EXPIRED = EnumField("expired", label=_("已过期"))


class CollaborationStrategyStatus(StrStructuredEnum):
    """协同策略状态"""

    ENABLED = EnumField("enabled", label=_("启用"))
    DISABLED = EnumField("disabled", label=_("禁用"))
    # 注：未确认只有接受方会有这个状态
    UNCONFIRMED = EnumField("unconfirmed", label=_("未确认"))


class CollaborationScopeType(StrStructuredEnum):
    """协同范围类型"""

    ALL = EnumField("all", label=_("全部"))
    # TODO (su) 支持指定协同的组织范围 & 用户字段
    # SPECIFIED = EnumField("specified", label=_("指定"))


class FieldMappingOperation(StrStructuredEnum):
    """字段映射关系"""

    DIRECT = EnumField("direct", label=_("直接"))
    EXPRESSION = EnumField("expression", label=_("表达式"))


class TenantUserIdRuleEnum(StrStructuredEnum):
    """租户用户 ID 生成规则"""

    NANOID = EnumField("nanoid", label=_("nanoid"))
    UUID4_HEX = EnumField("uuid4_hex", label=_("uuid4 hex"))
    USERNAME = EnumField("username", label=_("用户名"))
    USERNAME_WITH_DOMAIN = EnumField("username@domain", label=_("用户名@域名"))
