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
import json
import logging

from django.db import connections
from sentry_sdk import capture_exception

from bklogin.common.error_codes import error_codes
from bklogin.utils.std_error import APIError

from .response import APIErrorResponse

logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """
        对异常进行处理，使用蓝鲸 Http API 协议响应
        """
        error = _handle_exception(request, exception)

        # 根据蓝鲸新版HTTP API 协议， 处理响应数据
        #  开发者关注的，能自助排查, 快速定位问题
        detail = {"code": error.code, "message": ""}
        if error.detail and isinstance(error.detail, dict):
            detail.update(error.detail)

        return APIErrorResponse(
            code=error.code_category,
            message=error.message,
            system="bk-login",
            details=[detail],
            data=error.data or {},
            status=error.status_code,
        )


def _handle_exception(request, exc) -> APIError:
    """统一处理异常，并转换成 APIError"""
    if isinstance(exc, APIError):
        # 回滚事务
        _set_rollback()
        return exc

    # 非预期内的异常（1）记录日志（2）推送到 sentry (3) 以系统异常响应
    logger.exception(
        "catch unexpected error, request url->[%s], request method->[%s] request params->[%s]",
        request.path,
        request.method,
        json.dumps(getattr(request, request.method, None)),
    )

    # 推送异常到 sentry
    capture_exception(exc)

    # Note: 系统异常不暴露异常详情信息，避免敏感信息泄露
    return error_codes.SYSTEM_ERROR


def _set_rollback():
    """DB事务回滚"""
    for db in connections.all():
        if db.settings_dict["ATOMIC_REQUESTS"] and db.in_atomic_block:
            db.set_rollback(True)
