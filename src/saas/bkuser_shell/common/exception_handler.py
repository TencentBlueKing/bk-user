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
import logging

from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler
from sentry_sdk import capture_exception

from .error_codes import APIError

logger = logging.getLogger(__name__)


# 通用 HTTP 状态码
BK_GENERAL_STATUS_CODE = 200


def ee_exception_response(exc, context):
    """针对企业版异常返回封装"""
    data = {
        "result": False,
        "data": None,
    }

    logger.exception("request apiServer failed: ")

    if isinstance(exc, APIError):
        # 主动抛出的已知异常
        data.update({"code": exc.code_num, "message": exc.message})
    # FIXME: 无权限报错怎么提示的?
    # elif isinstance(exc, ApiException):
    #     # 后端返回的 API 异常
    #     parser = ApiExceptionParser(exc)
    #     if parser.get_code() == "PERMISSION_DENIED":
    #         data.update({"code": -1, "message": _("您没有权限访问该资源"), "detail": parser.get_message()})
    #         return Response(data=data, status=status.HTTP_403_FORBIDDEN)
    #     else:
    #         data.update({"code": -1, "message": parser.get_message()})

    elif isinstance(exc, Http404):
        data.update({"code": -1, "message": _("您要找的资源无法被找到")})
    elif isinstance(exc, PermissionDenied):
        data.update({"code": -1, "message": _("您没有执行该操作的权限")})
    elif isinstance(exc, ValidationError):
        data.update({"code": -1, "message": parse_validation_error(exc)})
    else:
        # report to sentry
        capture_exception(exc)

        # Call REST framework's default exception handler to get the standard error response.
        response = exception_handler(exc, context)
        if response is not None:
            response.data.update(code=-1)
        else:
            data = {"code": -1, "message": _("SaaS 后端服务异常，请检查日志以获得更多的信息")}
            response = Response(data, status=BK_GENERAL_STATUS_CODE)
        return response

    return Response(data=data, status=BK_GENERAL_STATUS_CODE)


def parse_validation_error(exc):
    error_messages = []
    for k, values in exc.detail.items():
        message = _("参数 {} 校验错误: {}").format(k, ",".join(values))
        error_messages.append(message)

    return "\n".join(error_messages)


# class ApiExceptionParser:
#     def __init__(self, exc):
#         self.exc = exc

#         if getattr(self.exc, "body", False):
#             try:
#                 self.body = json.loads(self.exc.body)
#             except Exception:  # pylint: disable=broad-except
#                 self.body = None
#         else:
#             self.body = None

#     def get_code(self) -> int:
#         if not self.body:
#             return -1

#         return self.body.get("code", -1)

#     def get_message(self) -> str:
#         # TODO: should expose the api error detail! currently, always be this message, not helpfully at all
#         if not self.body:
#             return _("API 服务返回异常，请检查 API 服务日志")

#         return self.body.get("detail") or _("API 服务返回异常，请检查 API 服务日志")
