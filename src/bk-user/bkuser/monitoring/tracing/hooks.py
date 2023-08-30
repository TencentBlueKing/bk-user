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
from typing import Dict

import requests
from django.http import HttpRequest, HttpResponse
from opentelemetry.trace import Span, StatusCode, format_trace_id
from rest_framework import status


def handle_api_error(span: Span, result: Dict):
    """统一处理新版 HTTP API 协议中的错误详情"""
    if "error" not in result:
        return

    err = result["error"]
    span.set_attribute("error_code", err.get("code", ""))
    span.set_attribute("error_message", err.get("message", ""))
    span.set_attribute("error_system", err.get("system", ""))
    # 错误详情若存在，则统一存到一个字段中
    if err_details := err.get("details", []):
        span.set_attribute("error_details", json.dumps(err_details))


def requests_response_hook(span: Span, request: requests.Request, response: requests.Response):
    """用于处理 requests 库发起的请求响应，需要兼容支持新旧 esb，apigw，新版 HTTP 协议"""
    if (
        # requests 请求异常, 例如访问超时等
        response is None
        # 并非所有返回内容都是 json 格式的, 因此需要根据返回头进行判断, 避免处理二进制格式的内容
        or response.headers.get("Content-Type") != "application/json"
    ):
        return

    try:
        result = json.loads(response.content)
    except Exception:  # pylint: disable=broad-except
        return
    if not isinstance(result, dict):
        return

    request_id = (
        # new esb and apigateway
        response.headers.get("x-bkapi-request-id")
        # legacy api
        or response.headers.get("X-Request-Id")
        # old esb and other
        or result.get("request_id", "")
    )
    if request_id:
        span.set_attribute("request_id", request_id)

    if "message" in result:
        span.set_attribute("error_message", result["message"])

    # 旧版本 API 中，code 为 0/'0'/'00' 表示成功
    code = result.get("code")
    if code is not None:
        span.set_attribute("error_code", str(code))
        if str(code) in ["0", "00"]:
            span.set_status(StatusCode.OK)
        else:
            span.set_status(StatusCode.ERROR)

        # 后续均为处理新版 API 协议逻辑，因此此处直接 return
        return

    # 根据新版本 HTTP API 协议，处理错误详情
    handle_api_error(span, result)

    if status.is_success(response.status_code):
        span.set_status(StatusCode.OK)
    else:
        span.set_status(StatusCode.ERROR)


def django_request_hook(span: Span, request: HttpRequest):
    """在 request 注入 trace_id，方便获取"""
    trace_id = span.get_span_context().trace_id
    request.otel_trace_id = format_trace_id(trace_id)


def django_response_hook(span: Span, request: HttpRequest, response: HttpResponse):
    """处理 Django 响应，因用户管理已经使用新版本 HTTP 协议，因此仅支持新版协议"""

    if (
        # requests 请求异常, 例如访问超时等
        response is None
        # 并非所有返回内容都是 json 格式的, 因此需要根据返回头进行判断, 避免处理二进制格式的内容
        or response.headers.get("Content-Type") != "application/json"
    ):
        return

    # 新版本协议中按照标准 HTTP 协议，200 <= code < 300 的都是正常
    if status.is_success(response.status_code):
        span.set_status(StatusCode.OK)
        return

    span.set_status(StatusCode.ERROR)
    try:
        result = json.loads(response.content)
    except Exception:  # pylint: disable=broad-except
        return
    if not isinstance(result, dict):
        return

    # 若能够获取到 request_id，则一并记录
    request_id = response.headers.get("X-Request-Id") or result.get("request_id")
    if request_id:
        span.set_attribute("request_id", request_id)

    handle_api_error(span, result)
