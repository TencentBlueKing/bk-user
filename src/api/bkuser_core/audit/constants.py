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


class LogInFailReason(AutoLowerEnum):
    BAD_PASSWORD = auto()
    EXPIRED_PASSWORD = auto()
    TOO_MANY_FAILURE = auto()
    LOCKED_USER = auto()
    DISABLED_USER = auto()
    DELETED_USER = auto()
    EXPIRED_USER = auto()
    RESIGNED_USER = auto()
    SHOULD_CHANGE_INITIAL_PASSWORD = auto()

    _choices_labels = (
        (BAD_PASSWORD, "密码错误"),
        (EXPIRED_PASSWORD, "密码过期"),
        (TOO_MANY_FAILURE, "密码错误次数过多"),
        (LOCKED_USER, "用户已锁定"),
        (DISABLED_USER, "用户已禁用"),
        (DELETED_USER, "用户已删除"),
        (EXPIRED_USER, "用户账号已过期"),
        (RESIGNED_USER, "用户已离职"),
        (SHOULD_CHANGE_INITIAL_PASSWORD, "需要修改初始密码"),
    )


class ResetPasswordFailReason(AutoLowerEnum):
    BAD_OLD_PASSWORD = auto()

    _choices_labels = ((BAD_OLD_PASSWORD, "原密码校验错误"),)


class OperationType(AutoLowerEnum):
    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()
    HARD_DELETE = auto()
    REVERT = auto()
    RETRIEVE = auto()

    SYNC = auto()
    IMPORT = auto()
    EXPORT = auto()
    RESTORATION = auto()

    FORGET_PASSWORD = auto()  # 用户通过 token 重置
    ADMIN_RESET_PASSWORD = auto()  # 管理员重置密码
    MODIFY_PASSWORD = auto()  # 用户通过旧密码修改

    SET_FIELD_VISIBLE = auto()  # 展示字段设置显示
    SET_FIELD_INVISIBLE = auto()  # 展示字段设置屏蔽

    _choices_labels = (
        (CREATE, "创建"),
        (UPDATE, "更新"),
        (DELETE, "删除"),
        (REVERT, "还原"),
        (HARD_DELETE, "硬删除"),
        (RETRIEVE, "获取"),
        (SYNC, "同步"),
        (EXPORT, "导出"),
        (IMPORT, "导入"),
        (RESTORATION, "恢复"),
        (FORGET_PASSWORD, "用户通过token重置密码"),
        (ADMIN_RESET_PASSWORD, "管理员重置密码"),
        (MODIFY_PASSWORD, "用户通过旧密码修改"),
        (SET_FIELD_VISIBLE, "设置字段展示"),
        (SET_FIELD_INVISIBLE, "设置字段隐藏"),
    )


class OperationStatus(AutoLowerEnum):
    SUCCEED = auto()
    FAILED = auto()

    _choices_labels = (
        (SUCCEED, "成功"),
        (FAILED, "失败"),
    )
