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
from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.http import HttpResponseForbidden
from django.http.request import HttpRequest
from django.utils.deprecation import MiddlewareMixin
from rest_framework.authentication import SessionAuthentication

logger = logging.getLogger(__name__)


APP_INFO_HEADER = "HTTP_X_APP_AUTH_INFO"
OPERATOR_HEADER = "HTTP_X_BKUSER_OPERATOR"


class AppLimiterMiddleware(MiddlewareMixin):
    """限制只有某些应用能够访问"""

    class AppAuthInfoLoader(object):
        def __init__(self, code, secret):
            if not code or not secret:
                raise ValueError("code secret is needed.")

            self.code = code
            self.secret = secret

        @classmethod
        def from_raw_info(cls, request):
            """GET 只能通过 URL params POST 需要将参数以 json 形式放到 body 中"""
            if request.method == "GET":
                code = request.GET.get("bk_app_code")
                secret = request.GET.get("bk_app_secret") or request.POST.get("bk_app_secret")
            elif request.method == "POST":
                body = json.loads(request.body)
                code = body.get("bk_app_code")
                secret = body.get("bk_app_secret")
            else:
                raise NotImplementedError("other method has not been supported yet")

            return cls(code, secret)

    def process_request(self, request):
        try:
            app_info = self.AppAuthInfoLoader.from_raw_info(request)
        except ValueError:
            return HttpResponseForbidden(content="only app in white list owns access.")

        try:
            assert settings.ACCESS_APP_WHITE_LIST[app_info.code] == app_info.secret, "check app code & secret failed."
        except KeyError:
            return HttpResponseForbidden(content="only app in white list owns access.")
        except AssertionError:
            return HttpResponseForbidden(content="check app code & secret mismatch.")
        except Exception:  # pylint: disable=broad-except
            logger.exception("check app code & secret failed.")
            return HttpResponseForbidden(content="check app code & secret failed.")


@dataclass
class RequestBaseInfo:
    remote_addr: str
    path_info: str
    request_id: str
    query_string: str
    method: str
    agent_header: str
    accept_language: str
    operator: Optional[str] = "nobody"

    __missing_term = "_MISSING_"

    @classmethod
    def from_request(cls, request: HttpRequest):
        return cls(
            remote_addr=request.META.get("REMOTE_ADDR", cls.__missing_term),
            path_info=request.META.get("PATH_INFO", "None"),
            request_id=request.META.get("HTTP_X_BKAPI_REQUEST_ID", cls.__missing_term),
            query_string=request.META.get("QUERY_STRING", "None"),
            method=request.META.get("REQUEST_METHOD", cls.__missing_term),
            agent_header=request.META.get("HTTP_USER_AGENT", cls.__missing_term),
            accept_language=request.META.get("HTTP_ACCEPT_LANGUAGE", cls.__missing_term),
        )

    def __str__(self):
        return (
            f"request<{self.request_id}> info: "
            f"Path({self.path_info}) with QueryString<{self.query_string}> via {self.method} "
            f"from RemoteAddr<{self.remote_addr}> Agent<{self.agent_header}> "
            f"AcceptLanguage<{self.accept_language}> Operator<{self.operator}>"
        )


class OperatorMiddleware(MiddlewareMixin):
    def get_operator_from_req(self, request: HttpRequest):
        # TODO: get operator from esb
        return request.META.get(OPERATOR_HEADER, "nobody")

    def process_request(self, request: HttpRequest):
        base_info = RequestBaseInfo.from_request(request)

        operator = self.get_operator_from_req(request)
        # 审计需要
        setattr(request, "operator", operator)

        base_info.operator = operator
        logger.info(base_info)
        return


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        # To not perform the csrf check previously happening
        return
