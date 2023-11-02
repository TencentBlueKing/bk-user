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
from typing import List, Optional

from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel, model_validator

from bkuser.apps.tenant.models import Tenant, TenantUserValidityPeriodConfig
from bkuser.common.error_codes import error_codes


class NotificationMethod(str, StructuredEnum):
    """通知方式"""

    EMAIL = EnumField("email", label=_("邮件通知"))
    SMS = EnumField("sms", label=_("短信通知"))


class NotificationScene(str, StructuredEnum):
    """通知场景"""

    ACCOUNT_EXPIRING = EnumField("account_expiring", label=_("临过期提醒"))
    ACCOUNT_EXPIRED = EnumField("account_expired", label=_("过期提醒"))


class NotificationTemplate(BaseModel):
    """通知模板"""

    # 通知方式 如短信，邮件
    method: NotificationMethod
    # 通知场景 如将过期，已过期
    scene: NotificationScene
    # 模板标题
    title: Optional[str] = None
    # 模板发送方
    sender: str
    # 模板内容（text）格式
    content: str
    # 模板内容（html）格式
    content_html: str

    @model_validator(mode="after")
    def validate_attrs(self) -> "NotificationTemplate":
        if self.method == NotificationMethod.EMAIL and not self.title:
            raise ValueError(_("邮件通知模板需要提供标题"))

        return self


class ValidityPeriodConfig(BaseModel):
    """账号有效期配置"""

    # 使能账号有效期设置
    enabled_validity_period: bool
    # 有效期，单位：天
    valid_time: int
    # 临X天过期发送提醒, 单位：天
    remind_before_expire: List[int]
    # 通知方式
    enabled_notification_methods: List[NotificationMethod]
    # 通知模板
    notification_templates: List[NotificationTemplate]


class TenantUserValidityPeriodConfigHandler:
    # 账户有效期配置初始化,默认值
    DEFAULT_TENANT_USER_VALIDITY_PERIOD_CONFIG = {
        "enabled_validity_period": True,
        "valid_time": -1,
        "remind_before_expire": [7],
        "enabled_notification_methods": [NotificationMethod.EMAIL],
        "notification_templates": [
            {
                "method": NotificationMethod.EMAIL,
                "scene": NotificationScene.ACCOUNT_EXPIRING,
                "title": "蓝鲸智云 - 账号即将到期提醒!",
                "sender": "蓝鲸智云",
                "content": (
                    "{{ username }}, 您好：\n"
                    + "您的蓝鲸智云平台账号将于 {{ expired_at }} 天后到期。"
                    + "为避免影响使用，请尽快联系平台管理员进行续期。\n"
                    + "此邮件为系统自动发送，请勿回复。\n"
                ),
                "content_html": (
                    "<p>{{ username }}, 您好：</p>"
                    + "<p>您的蓝鲸智云平台账号将于 {{ expired_at }} 天后到期。"
                    + "为避免影响使用，请尽快联系平台管理员进行续期。</p>"
                    + "<p>此邮件为系统自动发送，请勿回复。</p>"
                ),
            },
            {
                "method": NotificationMethod.EMAIL,
                "scene": NotificationScene.ACCOUNT_EXPIRED,
                "title": "蓝鲸智云 - 账号到期提醒!",
                "sender": "蓝鲸智云",
                "content": (
                    "{{ username }}，您好：\n"
                    + " 您的蓝鲸智云平台账号已过期。如需继续使用，请尽快联系平台管理员进行续期。\n"
                    + " 此邮件为系统自动发送，请勿回复。"
                ),
                "content_html": (
                    "<p>{{ username }}，您好：</p>"
                    + "<p>您的蓝鲸智云平台账号已过期，如需继续使用，请尽快联系平台管理员进行续期。</p>"
                    + "<p>此邮件为系统自动发送，请勿回复。</p>"
                ),
            },
            {
                "method": NotificationMethod.SMS,
                "scene": NotificationScene.ACCOUNT_EXPIRING,
                "title": None,
                "sender": "蓝鲸智云",
                "content": (
                    "{{ username }}，您好：\n"
                    + "您的蓝鲸智云平台账号将于 {{ expired_at }} 天后到期。"
                    + "为避免影响使用，请尽快联系平台管理员进行续期。\n"
                    + "该短信为系统自动发送，请勿回复。"
                ),
                "content_html": (
                    "<p>{{ username }}，您好：</p>"
                    + "<p>您的蓝鲸智云平台账号将于 {{ expired_at }} 天后到期。"
                    + "为避免影响使用，请尽快联系平台管理员进行续期。</p>"
                    + "<p>该短信为系统自动发送，请勿回复。</p>"
                ),
            },
            {
                "method": NotificationMethod.SMS,
                "scene": NotificationScene.ACCOUNT_EXPIRED,
                "title": None,
                "sender": "蓝鲸智云",
                "content": (
                    "{{ username }}，您好：\n "
                    + "您的蓝鲸智云平台账号已过期。如需继续使用，请尽快联系平台管理员进行续期。\n "
                    + "该短信为系统自动发送，请勿回复。"
                ),
                "content_html": (
                    "<p>{{ username }}您好：</p>"
                    + "<p>您的蓝鲸智云平台账号已过期，如需继续使用，请尽快联系平台管理员进行续期。</p>"
                    + "<p>该短信为系统自动发送，请勿回复。</p>"
                ),
            },
        ],
    }

    def init_tenant_user_validity_period_config(
        self,
        tenant_id: str,
        operator: str,
    ):
        """
        租户创建完成后， 初始化账户有效期设置
        """
        tenant = Tenant.objects.filter(id=tenant_id).first()
        if not tenant:
            raise error_codes.OBJECT_NOT_FOUND

        validity_period_config = self.DEFAULT_TENANT_USER_VALIDITY_PERIOD_CONFIG

        TenantUserValidityPeriodConfig.objects.create(
            tenant=tenant,
            enabled_validity_period=validity_period_config["enabled_validity_period"],
            valid_time=validity_period_config["valid_time"],
            remind_before_expire=validity_period_config["remind_before_expire"],
            enabled_notification_methods=validity_period_config["enabled_notification_methods"],
            notification_templates=validity_period_config["notification_templates"],
            updater=operator,
            creator=operator,
        )

    @staticmethod
    def update_tenant_user_validity_period_config(
        tenant_id: str, operator: str, validity_period_config: ValidityPeriodConfig
    ):
        instance = TenantUserValidityPeriodConfig.objects.filter(tenant_id=tenant_id).first()
        if not instance:
            raise error_codes.OBJECT_NOT_FOUND

        notification_templates = [item.model_dump() for item in validity_period_config.notification_templates]
        with transaction.atomic():
            instance.enabled_validity_period = validity_period_config.enabled_validity_period
            instance.valid_time = validity_period_config.valid_time
            instance.remind_before_expire = validity_period_config.remind_before_expire
            instance.enabled_notification_methods = validity_period_config.enabled_notification_methods
            instance.notification_templates = notification_templates
            instance.updater = operator
            instance.save()

    @staticmethod
    def get_tenant_user_validity_period_config(tenant_id: str) -> ValidityPeriodConfig:
        instance = TenantUserValidityPeriodConfig.objects.filter(tenant_id=tenant_id).first()
        if not instance:
            raise error_codes.OBJECT_NOT_FOUND

        return ValidityPeriodConfig(
            enabled_validity_period=instance.enabled_validity_period,
            valid_time=instance.valid_time,
            remind_before_expire=instance.remind_before_expire,
            enabled_notification_methods=instance.enabled_notification_methods,
            notification_templates=instance.notification_templates,
        )
