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


class SettingsEnableNamespaces(AutoLowerEnum):
    GENERAL = auto()
    PASSWORD = auto()
    CONNECTION = auto()
    FIELDS = auto()
    ACCOUNT = auto()

    _choices_labels = (
        (GENERAL, "通用"),
        (PASSWORD, "密码"),
        (CONNECTION, "连接"),
        (FIELDS, "字段"),
        (ACCOUNT, "账号"),
    )


class GlobalSettingsEnableNamespaces(AutoLowerEnum):
    GENERAL = auto()
    RECYCLING_STRATEGY = auto()

    _choices_labels = ((GENERAL, "通用"), (RECYCLING_STRATEGY, "回收策略"))


class InitPasswordMethod(AutoLowerEnum):
    FIXED_PRESET = auto()
    RANDOM_VIA_MAIL = auto()


ACCOUNT_EXPIRATION_NOTICE_INTERVAL_META_KEY = "account_expiration_notice_interval"
PASSWORD_EXPIRATION_NOTICE_INTERVAL_META_KEY = "password_expiration_notice_interval"
