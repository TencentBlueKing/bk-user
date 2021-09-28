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

RESET_PASSWORD_VAILD_MINUTES = 3 * 60


TOKEN_IS_OK = 0
TOKEN_USED_CODE = 10000
TOKEN_EXPIRED_CODE = 10001
TOKEN_PROFILE_NOT_EXIST_CODE = 10002
TOKEN_NOT_EXIST_CODE = 10003


class LogInFailReasonEnum(AutoLowerEnum):

    BAD_PASSWORD = auto()
    EXPIRED_PASSWORD = auto()
    TOO_MANY_FAILURE = auto()
    LOCKED_USER = auto()
    DISABLED_USER = auto()

    _choices_labels = (
        (BAD_PASSWORD, "密码错误"),
        (EXPIRED_PASSWORD, "密码过期"),
        (TOO_MANY_FAILURE, "密码错误次数过多"),
        (LOCKED_USER, "用户已锁定"),
        (DISABLED_USER, "用户已删除"),
    )


class OperationEnum(AutoLowerEnum):

    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()
    RETRIEVE = auto()

    SYNC = auto()
    IMPORT = auto()
    EXPORT = auto()
    RESTORATION = auto()

    _choices_labels = (
        (CREATE, "创建"),
        (UPDATE, "更新"),
        (DELETE, "删除"),
        (RETRIEVE, "获取"),
        (SYNC, "同步"),
        (EXPORT, "导出"),
        (IMPORT, "导入"),
        (RESTORATION, "恢复"),
    )
