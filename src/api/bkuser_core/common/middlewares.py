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

if TYPE_CHECKING:
    from django.http import HttpRequest
    from rest_framework.response import Response

logger = logging.getLogger(__name__)


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


# FIXME: remove this, all use ee_format for now!
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

    def _force_ee_response(self, resp: "Response") -> "Response":
        """强制刷返回值"""
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
