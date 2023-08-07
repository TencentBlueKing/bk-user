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

from blue_krill.web.drf_utils import stringify_validation_error
from django.conf import settings
from django.http.response import Http404, HttpResponseNotFound
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic.base import TemplateView
from rest_framework.exceptions import (
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    ParseError,
    PermissionDenied,
    UnsupportedMediaType,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import set_rollback
from sentry_sdk import capture_exception

from bkuser.common.error_codes import error_codes
from bkuser.utils.std_error import APIError

logger = logging.getLogger(__name__)


def one_line_error(error: ValidationError):
    """Extract one line error from ValidationError"""
    try:
        return stringify_validation_error(error)[0]
    except Exception:
        logger.exception("Error getting one line error from %s", error)
        return "param format error"


def _handle_exception(request, exc) -> APIError:
    """统一处理异常，并转换成 APIError"""
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return error_codes.UNAUTHENTICATED

    if isinstance(exc, PermissionDenied):
        return error_codes.NO_PERMISSION.f(exc.detail)

    if isinstance(exc, (NotFound, Http404)):
        return error_codes.OBJECT_NOT_FOUND

    if isinstance(exc, (MethodNotAllowed, ParseError, UnsupportedMediaType)):
        return error_codes.INVALID_ARGUMENT.f(exc.detail)

    if isinstance(exc, ValidationError):
        error_codes.VALIDATION_ERROR.f(one_line_error(exc)).set_detail({"message": json.dumps(exc.detail)})

    if isinstance(exc, APIError):
        # 回滚事务
        set_rollback()
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


def custom_exception_handler(exc, context):
    """
    Use a standard error response instead of REST Framework's default behaviour
    {
      "code": "ERROR_CODE_CATEGORY",
      "message": "error message",
      "system": "current system",
      "data": {...},  # Used to allow the caller to perform some corresponding actions based on this code
      "detail": [{code: "ERROR_CODE", "message": "", ...}]
    }
    """
    request = context["request"]
    error = _handle_exception(request, exc)

    # 根据蓝鲸新版HTTP API 协议， 处理响应数据
    #  开发者关注的，能自助排查, 快速定位问题
    detail = {"code": error.code, "message": ""}
    if error.detail and isinstance(error.detail, dict):
        detail.update(error.detail)

    data = {
        # 普通用户只关注错误的大类
        "code": error.code_category,
        "message": error.message,
        "system": "bk-user",
        "details": [detail],
        "data": error.data or {},
    }

    return Response(data=data, status=error.status_code)


class VueTemplateView(TemplateView):
    template_name = "index.html"

    @xframe_options_exempt
    def get(self, request, *args, **kwargs):
        # 尝试获取模板，找不到模板，则404
        try:
            get_template(self.template_name)
        except TemplateDoesNotExist:
            return HttpResponseNotFound("Not Found")

        # Context
        try:
            context = {
                # BK_DOMAIN
                "BK_DOMAIN": settings.BK_DOMAIN,
                "BK_USER_URL": settings.BK_USER_URL.rstrip("/"),
                "AJAX_BASE_URL": settings.AJAX_BASE_URL.rstrip("/"),
                # 去除末尾的 /, 前端约定
                "STATIC_URL": settings.STATIC_URL.rstrip("/"),
                # 去除开头的 . document.domain需要
                "SESSION_COOKIE_DOMAIN": settings.SESSION_COOKIE_DOMAIN.lstrip("."),
                # csrftoken name
                "CSRF_COOKIE_NAME": settings.CSRF_COOKIE_NAME,
                "BK_COMPONENT_API_URL": settings.BK_COMPONENT_API_URL.rstrip("/"),
            }

        except Exception:  # pylint: disable=broad-except
            logger.exception("get context for index.html failed")
            context = {}

        kwargs.update(context)

        return super(VueTemplateView, self).get(request, *args, **kwargs)
