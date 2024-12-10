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
import base64
import json
import logging
from collections import namedtuple
from typing import Any, Dict

import jwt
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
        error = _handle_exception(request, exception)

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
    """DB 事务回滚"""
    for db in connections.all():
        if db.settings_dict["ATOMIC_REQUESTS"] and db.in_atomic_block:
            db.set_rollback(True)


class APIGatewayJWTMiddleware:
    """
    该中间件读取由 API 网关传输的 JWT 头信息，获取相应的公钥进行解密，将解密结果赋值给 request.app。
    默认情况下，通过 settings.BK_APIGW_PUBLIC_KEY 读取 API 网关公钥
    """

    JWT_KEY_HEADER_NAME = "HTTP_X_BKAPI_JWT"
    ALGORITHM = "RS512"
    App = namedtuple("App", ["bk_app_code", "verified"])

    def __init__(self, get_response):
        self.get_response = get_response

        self.public_key = self._get_public_key()

    def __call__(self, request):
        # 解析 Header 头 APIGateway JWT
        jwt_token = request.META.get(self.JWT_KEY_HEADER_NAME, "")
        jwt_payload = self._decode_jwt(jwt_token)
        if not jwt_payload:
            return self.get_response(request)

        # App 信息
        jwt_app = jwt_payload.get("app") or {}
        bk_app_code = jwt_app.get("bk_app_code", jwt_app.get("app_code", None))
        app_verified = jwt_app.get("verified", False)

        # 将 JWT App 信息赋值给 request.app
        request.app = self._make_app(bk_app_code=bk_app_code, verified=app_verified)

        return self.get_response(request)

    @staticmethod
    def _get_public_key():
        """
        获取 APIGW 的 Public Key
        由于配置文件里的 public key 是来自环境变量，且使用 base64 编码，因此需要解码
        """
        if not settings.BK_APIGW_PUBLIC_KEY:
            logger.error("setting `BK_APIGW_PUBLIC_KEY` can not be empty")
            return ""

        try:
            return base64.b64decode(settings.BK_APIGW_PUBLIC_KEY).decode("utf-8")
        except (TypeError, ValueError):
            logger.exception(
                "setting `BK_APIGW_PUBLIC_KEY` must be base64 string, BK_APIGW_PUBLIC_KEY=%s",
                settings.BK_APIGW_PUBLIC_KEY,
            )

        return ""

    def _decode_jwt(self, jwt_token: str) -> Dict[str, Any] | None:
        """
        解析 JWT
        :return
        {
          "app" : {"app_code" : "app-code-test", "verified" : true, ...},
          "user" : {"username" : "user-test", "verified" : false, ...}
        }
        """
        if not jwt_token:
            return None

        if not self.public_key:
            return None

        try:
            # 从 JWT 里的 Header 字段里解析出未验证的信息，比如算法，然后用于后续解析 JWT 里的 Payload
            jwt_header = jwt.get_unverified_header(jwt_token)
            algorithm = jwt_header.get("alg") or self.ALGORITHM
            # Note: bk apigw 目前的 issuer 不规范，所以这里不强校验 issuer
            return jwt.decode(jwt_token, self.public_key, algorithms=[algorithm], options={"verify_iss": False})
        except jwt.PyJWTError:
            logger.exception("jwt decode failed, jwt content: %s", jwt_token)

        return None

    def _make_app(self, bk_app_code=None, verified=False):
        return self.App(bk_app_code=bk_app_code, verified=verified)
