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
from typing import TYPE_CHECKING

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

if TYPE_CHECKING:
    from django.http import HttpRequest
    from rest_framework.response import Response

logger = logging.getLogger(__name__)


class BKLanguageMiddleware(MiddlewareMixin):
    """
    支持Header为Blueking-Language的语言设置
    翻译默认是通过django.middleware.locale.LocaleMiddleware中间件来实现的
    但是LocaleMiddleware中间件里优先对Cookie里语言，再对Header为Accept-Language的值
    这里通过使用Blueking-Language值替换Accept-Language的值来达到设置语言的目的
    Note: BKLanguageMiddleware 必须配置在django.middleware.locale.LocaleMiddleware之前
    """

    BK_LANGUAGE_HEADER = "HTTP_BLUEKING_LANGUAGE"
    LANGUAGE_HEADER = "HTTP_ACCEPT_LANGUAGE"

    def process_request(self, request):
        bk_language = request.META.get(self.BK_LANGUAGE_HEADER)
        if bk_language:
            # Note: bk_language 优先级高于默认的
            request.META[self.LANGUAGE_HEADER] = bk_language


class MethodOverrideMiddleware(MiddlewareMixin):
    METHOD_OVERRIDE_HEADER = "HTTP_X_HTTP_METHOD_OVERRIDE"

    def process_request(self, request):
        """因为 GET 方法 URL 长度有限制，可以使用 POST 实现 GET 效果"""
        if request.method == "POST" and self.METHOD_OVERRIDE_HEADER in request.META:
            request.method = request.META[self.METHOD_OVERRIDE_HEADER]

            if request.body:
                request_get_params = request.GET

                original_mutable = request_get_params._mutable
                request_get_params._mutable = True

                request_post_body = json.loads(request.body)
                request_get_params.update(request_post_body)

                # 恢复初始的_mutable属性
                request_get_params._mutable = original_mutable


class DynamicResponseFormatMiddleware:
    """根据动态修改返回值格式
    - 原生格式
    - 企业版包装格式
    """

    def _should_use_raw_response(self, req: "HttpRequest", resp: "Response") -> bool:
        """是否应该使用原生格式返回"""
        # 非 API 请求不包装返回值
        # NOTE: 目前有环境调用/api/v2/profiles/用到通过header强制使用raw response, 所以暂时不能去掉
        if not req.path.startswith("/api/"):
            return True

        # 通过 Header 判断是否强制使用原生格式
        if bool(req.META.get(settings.FORCE_RAW_RESPONSE_HEADER)):
            return True

        return False

    def _is_response_ee_format(self, resp: "Response") -> bool:
        """返回值是否符合企业版格式"""
        if getattr(resp, "data", None) is None:
            return False

        required_keys = ["result", "message", "code", "data"]
        for key in required_keys:
            if key not in resp.data:
                return False

        return True

    def _force_ee_response(self, resp: "Response") -> "Response":
        """强制刷返回值"""
        if self._is_response_ee_format(resp):
            return resp

        # 来自缓存的 response 没有对应属性
        # 由于 response 已经被渲染，并不需要 callback
        force_data = {"result": True, "code": 0, "message": "success", "data": getattr(resp, "data", None)}

        if not getattr(resp, "_post_render_callbacks", None):
            resp._post_render_callbacks = []

        resp.data = force_data
        resp._is_rendered = False

        # templateResponse has no render, which we won't care
        if not getattr(resp, "render", False):
            return resp

        resp.render()
        return resp

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # 204 无内容不需要包装, 强制渲染会导致204卡主(一直不结束)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            return response

        # exception handler 将添加标记, 避免重复处理
        if getattr(response, "from_exception", None):
            return response

        # for excel export
        if response.headers.get("Content-Type", "") == "application/ms-excel":
            return response

        if self._should_use_raw_response(request, response):
            return response
        else:
            return self._force_ee_response(response)
