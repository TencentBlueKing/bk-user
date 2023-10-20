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

from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _

# 本地数据源密码最大长度
MAX_PASSWORD_LENGTH = 32

# 永远不会过期的时间标识
NEVER_EXPIRE_TIME = -1

# 每一天的秒数
ONE_DAY_SECONDS = 24 * 60 * 60

# 密码可选最长有效期：10年
MAX_PASSWORD_VALID_TIME = 10 * 365

# 可选最长锁定时间：10年
MAX_LOCK_TIME = 10 * 365 * ONE_DAY_SECONDS

# 连续性限制上限
MAX_NOT_CONTINUOUS_COUNT = 10

# 重试密码次数上限
PASSWORD_MAX_RETRIES = 10

# 保留的历史密码上限
MAX_RESERVED_PREVIOUS_PASSWORD_COUNT = 5

# 数据源用户名规则
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{1,30}[a-zA-Z0-9]$")


class PasswordGenerateMethod(str, StructuredEnum):
    """密码生成方式"""

    RANDOM = EnumField("random", label=_("随机生成"))
    FIXED = EnumField("fixed", label=_("固定值"))


class NotificationMethod(str, StructuredEnum):
    """通知方式"""

    EMAIL = EnumField("email", label=_("邮件通知"))
    SMS = EnumField("sms", label=_("短信通知"))


class NotificationScene(str, StructuredEnum):
    """通知场景"""

    USER_INITIALIZE = EnumField("user_initialize", label=_("用户初始化"))
    RESET_PASSWORD = EnumField("reset_password", label=_("重置密码"))
    PASSWORD_EXPIRING = EnumField("password_expiring", label=_("密码即将过期"))
    PASSWORD_EXPIRED = EnumField("password_expired", label=_("密码过期"))
