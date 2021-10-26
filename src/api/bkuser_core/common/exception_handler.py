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

from bkuser_core.bkiam.exceptions import IAMPermissionDenied
from django.core.exceptions import PermissionDenied
from django.db import ProgrammingError
from django.http import Http404
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import exception_handler

from .error_codes import CoreAPIError
from .http import exist_force_raw_header

logger = logging.getLogger(__name__)


# 企业版通用 HTTP 状态码
EE_GENERAL_STATUS_CODE = 200
UNKNOWN_ERROR_HINT = "request failed, please check api log of bk-user"


def custom_exception_handler(exc, context):
    """
    Use a standard error response instead of REST Framework's default behaviour
    """

    # {
    #     "code": "ERROR_CODE",
    #     # String
    #     "detail": "ERROR_DETAILS"
    #     # Only presents in ValidationError
    #     "fields_detail": {"field1": ["error message"]}
    # }
    if exist_force_raw_header(context["request"]):
        return get_raw_exception_response(exc, context)
    else:
        return get_ee_exception_response(exc, context)


def get_ee_exception_response(exc, context):
    """针对企业版异常返回封装"""
    data = {"result": False, "data": None, "code": -1}

    if isinstance(exc, CoreAPIError):
        # 主动抛出的已知异常
        data["code"] = exc.code_num
        data["message"] = exc.message
    elif isinstance(exc, Http404):
        data["message"] = "404, could not be found"
    elif isinstance(exc, PermissionDenied):
        data["message"] = "403, permission denied"
    elif isinstance(exc, IAMPermissionDenied):
        data["message"] = exc.extra_info
    elif isinstance(exc, ValidationError):
        data["message"] = f"validation error: {exc}"
    elif isinstance(exc, AuthenticationFailed):
        data["message"] = "403, authentication failed"
    else:
        logger.exception("request apiServer failed")
        data["message"] = UNKNOWN_ERROR_HINT
        data["code"] = -1

        # Call REST framework's default exception handler to get the standard error response.
        response = exception_handler(exc, context)
        if response is not None:
            response.data = data
            setattr(response, "from_exception", True)
            return response

    logger.exception("request apiServer failed")
    response = Response(data=data, status=EE_GENERAL_STATUS_CODE)
    setattr(response, "from_exception", True)
    return response


def one_line_error(detail):
    """Extract one line error from error dict"""
    try:
        # A bare ValidationError will result in a list "detail" field instead of a dict
        if isinstance(detail, list):
            return detail[0]
        else:
            key, (first_error, *_) = next(iter(detail.items()))
            if key == "non_field_errors":
                return first_error
            return f"{key}: {first_error}"
    except Exception:  # pylint: disable=broad-except
        return "参数格式错误"


def get_raw_exception_response(exc, context):
    if isinstance(exc, ValidationError):
        data = {
            "code": "VALIDATION_ERROR",
            "detail": one_line_error(exc.detail),
            "fields_detail": exc.detail,
        }
        return Response(data, status=exc.status_code, headers={})
    elif isinstance(exc, CoreAPIError):
        data = {
            "code": exc.code.code_name,
            "detail": exc.code.message,
        }
        return Response(data, status=exc.code.status_code, headers={})
    elif isinstance(exc, IAMPermissionDenied):
        data = {"code": "PERMISSION_DENIED", "detail": exc.extra_info}
        return Response(data, status=exc.status_code, headers={})
    elif isinstance(exc, ProgrammingError):
        logger.exception("occur some programming errors")
        data = {"code": "PROGRAMMING_ERROR", "detail": UNKNOWN_ERROR_HINT}
        return Response(data, status=HTTP_400_BAD_REQUEST, headers={})

    # Call REST framework's default exception handler to get the standard error response.
    response = exception_handler(exc, context)
    # Use a default error code
    if response is not None:
        response.data.update(code="ERROR")
        setattr(response, "from_exception", True)

    return response
