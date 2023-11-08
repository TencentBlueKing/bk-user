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
from typing import Optional

from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel, model_validator


class NotificationMethod(str, StructuredEnum):
    """通知方式"""

    EMAIL = EnumField("email", label=_("邮件通知"))
    SMS = EnumField("sms", label=_("短信通知"))


class NotificationScene(str, StructuredEnum):
    """通知场景"""

    TENANT_USER_EXPIRING = EnumField("tenant_user_expiring", label=_("租户用户-临过期提醒"))
    TENANT_USER_EXPIRED = EnumField("tenant_user_expired", label=_("租户用户-过期提醒"))


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
