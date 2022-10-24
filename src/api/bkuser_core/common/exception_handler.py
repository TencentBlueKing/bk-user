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
import traceback

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler
from sentry_sdk import capture_exception

from .error_codes import CoreAPIError
from bkuser_core.bkiam.exceptions import IAMPermissionDenied

logger = logging.getLogger(__name__)


# 企业版通用 HTTP 状态码
EE_GENERAL_STATUS_CODE = 200
UNKNOWN_ERROR_HINT = "request failed, please check api log of bk-user! "


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
    # extra details
    detail = {
        "error": "unknown",
    }
    if context:
        try:
            req = context.get("request")
            detail["path"] = req.path
            detail["method"] = req.method
            detail["query_params"] = req.query_params
            detail["request_id"] = req.headers.get("X-Request-Id")
            if hasattr(req, "bk_app_code"):
                detail["bk_app_code"] = req.bk_app_code
        except Exception:  # pylint: disable=broad-except
            # do nothing if get extra details fail
            pass

    # if bool(context["request"].META.get(settings.FORCE_RAW_RESPONSE_HEADER)):
    #     return get_raw_exception_response(exc, context, detail)
    # else:
    #     return get_ee_exception_response(exc, context, detail)
    return get_ee_exception_response(exc, context, detail)


def get_ee_exception_response(exc, context, detail):
    """针对企业版异常返回封装"""
    data = {"result": False, "data": None, "code": -1}

    if isinstance(exc, CoreAPIError):
        # 主动抛出的已知异常
        data["code"] = exc.code_num
        data["message"] = exc.message
        data["data"] = exc.data or None
    elif isinstance(exc, Http404):
        data["message"] = "404, could not be found"
    elif isinstance(exc, PermissionDenied):
        data["message"] = "403, permission denied"
    elif isinstance(exc, IAMPermissionDenied):
        data["message"] = _("您没有权限访问该资源")
        data["detail"] = exc.extra_info
        # saas给前端的判定数据结构: {"code": -1, "message": _("您没有权限访问该资源"), "detail": }
        # data = {"code": "PERMISSION_DENIED", "detail": exc.extra_info}
        # return Response(data, status=exc.status_code, headers={})
    elif isinstance(exc, ValidationError):
        data["message"] = f"validation error: {exc}"
    elif isinstance(exc, AuthenticationFailed):
        data["message"] = "403, authentication failed"
    else:
        # log
        logger.exception("unknown exception while handling the request, detail=%s", detail)
        # report to sentry
        capture_exception(exc)
        # build response
        data["message"] = UNKNOWN_ERROR_HINT
        # 如果有错误堆栈, 直接把堆栈暴露出来
        if exc is not None:
            data["message"] = UNKNOWN_ERROR_HINT + traceback.format_exc()
        data["code"] = -1

        # Call REST framework's default exception handler to get the standard error response.
        response = exception_handler(exc, context)
        if response is not None:
            response.data = data
            setattr(response, "from_exception", True)
            return response

    response = Response(data=data, status=EE_GENERAL_STATUS_CODE)
    setattr(response, "from_exception", True)
    return response
