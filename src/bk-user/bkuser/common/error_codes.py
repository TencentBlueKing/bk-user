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
from http import HTTPStatus
from enum import Enum

from bkuser.utils.std_error import ErrorCode
from django.utils.translation import gettext_lazy as _


class ErrorCodeCategoryEnum(Enum):
    # 400
    INVALID_ARGUMENT = 'INVALID_ARGUMENT'
    INVALID_REQUEST = 'INVALID_REQUEST'
    OUT_OF_RANGE = 'OUT_OF_RANGE'
    FAILED_PRECONDITION = 'FAILED_PRECONDITION'
    # 401
    UNAUTHENTICATED = 'UNAUTHENTICATED'
    # 403
    IAM_NO_PERMISSION = 'IAM_NO_PERMISSION'
    NO_PERMISSION = 'NO_PERMISSION'
    # 404
    NOT_FOUND = 'NOT_FOUND'
    # 409
    ALREADY_EXISTS = 'ALREADY_EXISTS'
    ABORTED = 'ABORTED'
    # 429
    RATE_LIMIT_EXCEED = 'RATE_LIMIT_EXCEED'
    RESOURCE_EXHAUSTED = 'RESOURCE_EXHAUSTED'
    # 500
    INTERNAL = 'INTERNAL'
    UNKNOWN = 'UNKNOWN'
    # 501
    NOT_IMPLEMENTED = 'NOT_IMPLEMENTED'


class ErrorCodes:
    # 通用
    INVALID_ARGUMENT = ErrorCode(_('参数非法'))
    UNAUTHENTICATED = ErrorCode(
        _('未认证'),
        code_category=ErrorCodeCategoryEnum.UNAUTHENTICATED.value,
        status_code=HTTPStatus.UNAUTHORIZED,
    )
    NO_PERMISSION = ErrorCode(
        _('无权限'),
        code_category=ErrorCodeCategoryEnum.NO_PERMISSION.value,
        status_code=HTTPStatus.FORBIDDEN,
    )
    OBJECT_NOT_FOUND = ErrorCode(
        _('对象未找到'),
        code_category=ErrorCodeCategoryEnum.NOT_FOUND.value,
        status_code=HTTPStatus.NOT_FOUND,
    )
    VALIDATION_ERROR = ErrorCode(_('参数校验不通过'))
    SYSTEM_ERROR = ErrorCode(
        _('系统异常'),
        code_category=ErrorCodeCategoryEnum.INTERNAL.value,
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )
    # 调用外部系统API
    REMOTE_REQUEST_ERROR = ErrorCode(_('调用外部系统API异常'))
    # 数据源
    DATA_SOURCE_TYPE_NOT_SUPPORTED = ErrorCode(_('数据源类型不支持'))


# 实例化一个全局对象
error_codes = ErrorCodes()
