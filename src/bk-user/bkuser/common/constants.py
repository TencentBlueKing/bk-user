# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import datetime

import pytz
from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _


class BkLanguageEnum(str, StructuredEnum):
    ZH_CN = EnumField("zh-CN", label="中文")
    EN = EnumField("en-US", label="英文")


class BKNonEntityUser(str, StructuredEnum):
    """蓝鲸非实体用户，主要用于 API 调用时的审计，区别于正常的实体用户"""

    # 用于 API 调用时，ESB / APIGW 传递过来的 jwt.user.verified 为 False 时，
    # jwt.user.username 是不可信的，有可能是很随意的字符串，所以用 BK__UNVERIFIED_USER 统一表示这类用户
    BK__UNVERIFIED_USER = EnumField("bk__unverified_user", label=_("未认证的用户"))
    # 用于 API 调用时，ESB / APIGW 传递过来的 jwt.user 为空时，但审计等其他场景需要做标识
    BK__ANONYMOUS_USER = EnumField("bk__anonymous_user", label=_("匿名用户"))


# 永久：2100-01-01 00:00:00 UTC
PERMANENT_TIME = datetime.datetime(year=2100, month=1, day=1, hour=0, minute=0, second=0, tzinfo=datetime.timezone.utc)

# 敏感信息掩码（7 位 * 是故意的，避免遇到用户输入 6/8 位 * 的情况）
SENSITIVE_MASK = "*******"

TIME_ZONE_CHOICES = [(i, i) for i in list(pytz.all_timezones)]

# datetime 对比时允许最大偏移的秒数内认为是相等的，默认 2 分钟
ALLOWED_DATETIME_MAX_OFFSET = 120
