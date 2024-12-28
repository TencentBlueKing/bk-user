# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
import json
import logging
from collections import namedtuple

from django.conf import settings
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
        error = self._handle_exception(request, exception)

        # 根据蓝鲸新版 HTTP API 协议，处理响应数据
        #  开发者关注的，能自助排查，快速定位问题
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

    def _handle_exception(self, request, exc) -> APIError:
        """统一处理异常，并转换成 APIError"""
        if isinstance(exc, APIError):
            # 回滚事务
            self._set_rollback()
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

    @staticmethod
    def _set_rollback():
        """DB 事务回滚"""
        for db in connections.all():
            if db.settings_dict["ATOMIC_REQUESTS"] and db.in_atomic_block:
                db.set_rollback(True)


class InnerBearerTokenMiddleware:
    keyword = "Bearer"
    InnerBearerToken = namedtuple("InnerBearerToken", ["verified"])

    def __init__(self, get_response):
        self.get_response = get_response

        self.allowed_token = [settings.BK_APIGW_TO_BK_USER_INNER_BEARER_TOKEN]

    def __call__(self, request):
        # 从请求头中获取 InnerBearerToken
        auth = request.META.get("HTTP_AUTHORIZATION", "").split()

        if not auth or auth[0].lower() != self.keyword.lower() or len(auth) != 2:  # noqa: PLR2004
            return self.get_response(request)

        token = auth[1]
        # 验证 InnerBearerToken 是否合法
        if token not in self.allowed_token:
            return self.get_response(request)

        # 设置 InnerBearerToken
        request.inner_bearer_token = self.InnerBearerToken(verified=True)

        return self.get_response(request)


class BkUserAppMiddleware:
    app_code_header = "HTTP_X_BK_APP_CODE"
    app_secret_header = "HTTP_X_BK_APP_SECRET"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 从请求头中获取 app_code / app_secret
        app_code = request.META.get(self.app_code_header)
        app_secret = request.META.get(self.app_secret_header)

        # 校验是否 BkUser App
        if (app_code, app_secret) != (settings.BK_USER_APP_CODE, settings.BK_USER_APP_SECRET):
            return self.get_response(request)

        # 设置 BkUser App 标记
        request.bk_user_app_verified = True

        return self.get_response(request)
