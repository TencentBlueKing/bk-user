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
from enum import Enum, auto

import pytz

from bkuser_core.common.enum import AutoLowerEnum, AutoNameEnum, ChoicesEnum


class ProfileStatus(AutoNameEnum):
    NORMAL = auto()
    LOCKED = auto()
    DELETED = auto()
    DISABLED = auto()
    EXPIRED = auto()

    _choices_labels = ((NORMAL, "正常"), (LOCKED, "被冻结"), (DELETED, "被删除"), (DISABLED, "被禁用"), (EXPIRED, "已过期"))


class StaffStatus(AutoNameEnum):
    IN = auto()
    OUT = auto()

    _choices_labels = ((IN, "在职"), (OUT, "离职"))


class PositionEnum(Enum):
    STAFF = 0
    GROUP_LEADER = 1

    _choices_labels = [(STAFF, "员工"), (GROUP_LEADER, "组长")]

    @classmethod
    def get_choices(cls):
        return cls._choices_labels.value


class RoleCodeEnum(ChoicesEnum):
    STAFF = 0
    SUPERUSER = 1
    DEVELOPER = 2
    OPERATOR = 3
    AUDITOR = 4

    _choices_labels = (
        (STAFF, "普通用户"),
        (SUPERUSER, "超级管理员"),
        (DEVELOPER, "开发者"),
        (OPERATOR, "职能化用户"),
        (AUDITOR, "审计员"),
    )


class LanguageEnum(ChoicesEnum):
    ZH_CN = "zh-cn"
    EN = "en"

    _choices_labels = ((ZH_CN, "中文"), (EN, "英文"))


TIME_ZONE_LIST = pytz.common_timezones
TIME_ZONE_CHOICES = [(i, i) for i in TIME_ZONE_LIST]


class PasswdValidityPeriodEnum(ChoicesEnum):
    ONE_MONTH = 30
    THREE_MONTHS = 90
    HALF_YEAR = 180
    ONE_YEAR = 365
    UNLIMITED = -1

    _choices_labels = (
        (ONE_MONTH, "一个月"),
        (THREE_MONTHS, "三个月"),
        (HALF_YEAR, "半年"),
        (ONE_YEAR, "一年"),
        (UNLIMITED, "永久"),
    )


class DynamicFieldTypeEnum(AutoLowerEnum):
    # TODO： 连同前端需要重构
    STRING = auto()
    ONE_ENUM = auto()
    MULTI_ENUM = auto()
    NUMBER = auto()
    TIMER = auto()

    _choices_labels = (
        (STRING, "字符串"),
        (ONE_ENUM, "枚举"),
        (MULTI_ENUM, "多枚举"),
        (NUMBER, "数值"),
        (TIMER, "日期"),
    )


class FieldMapMethod(AutoLowerEnum):
    DIRECT = auto()
    CUSTOM = auto()

    _choices_labels = (
        (DIRECT, "直接映射"),
        (CUSTOM, "自定义映射"),
    )


class TypeOfExpiration(AutoLowerEnum):
    ACCOUNT_EXPIRATION = auto()
    PASSWORD_EXPIRATION = auto()

    _choices_labels = (
        (ACCOUNT_EXPIRATION, "账号过期"),
        (PASSWORD_EXPIRATION, "密码过期"),
    )


PASSWD_RESET_VIA_SAAS_EMAIL_TMPL = "您的蓝鲸账号【{username}】的密码已被重置，若非本人操作，请及时修改"

NOTICE_METHOD_EMAIL = "send_email"
NOTICE_METHOD_SMS = "send_sms"
