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
from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _


class NotificationMethod(str, StructuredEnum):
    """通知方式"""

    EMAIL = EnumField("email", label=_("邮件"))
    SMS = EnumField("sms", label=_("短信"))


class NotificationScene(str, StructuredEnum):
    """通知场景"""

    USER_INITIALIZE = EnumField("user_initialize", label=_("用户初始化"))
    RESET_PASSWORD = EnumField("reset_password", label=_("重置密码"))
    PASSWORD_EXPIRING = EnumField("password_expiring", label=_("密码即将过期"))
    PASSWORD_EXPIRED = EnumField("password_expired", label=_("密码已过期"))
    MANAGER_RESET_PASSWORD = EnumField("manager_reset_password", label=_("管理员重置密码"))
    TENANT_USER_EXPIRING = EnumField("tenant_user_expiring", label=_("租户用户即将过期"))
    TENANT_USER_EXPIRED = EnumField("tenant_user_expired", label=_("租户用户已过期"))
