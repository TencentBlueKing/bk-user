# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json
from http import HTTPStatus
from typing import Collection

from django.conf import settings
from opentelemetry.instrumentation import dbapi
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor  # type: ignore
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.trace import Span, Status, StatusCode, format_trace_id


def requests_callback(span: Span, response):
    """
    处理蓝鲸标准协议响应
    """
    # requests 请求异常, 例如访问超时等
    if response is None:
        return

    # 并非所有返回内容都是 json 格式的, 因此需要根据返回头进行判断, 避免处理二进制格式的内容
    if response.headers.get("Content-Type") != "application/json":
        return

    try:
        json_result = response.json()
    except Exception:  # pylint: disable=broad-except
        return

    if not isinstance(json_result, dict):
        return

    # NOTE: esb got a result, but apigateway got not result
    # only 200 will do those check and set
    if response.status_code == HTTPStatus.OK:
        code = json_result.get("code", 0)
        try:
            code = int(code)
        except Exception:  # pylint: disable=broad-except
            pass
        span.set_attribute("result_code", code)
        if code in [0, "0", "00"]:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR))

    span.set_attribute("result_message", json_result.get("message", ""))

    errors = str(json_result.get("errors", ""))
    if errors:
        span.set_attribute("result_errors", errors)

    request_id = (
        # new esb and apigateway
        response.headers.get("x-bkapi-request-id")
        # old esb
        or json_result.get("request_id", "")
    )
    if request_id:
        span.set_attribute("request_id", request_id)


def django_request_hook(span, request):
    """
    在 request 注入 trace_id，方便获取
    """
    trace_id = span.get_span_context().trace_id
    request.otel_trace_id = format_trace_id(trace_id)


def django_response_hook(span, request, response):
    """
    处理蓝鲸标准协议 Django 响应
    """
    if (
        # requests 请求异常, 例如访问超时等
        response is None
        # 并非所有返回内容都是 json 格式的, 因此需要根据返回头进行判断, 避免处理二进制格式的内容
        or response.headers.get("Content-Type") != "application/json"
        # the status of non-200 should not be changed
        or response.status_code != HTTPStatus.OK
    ):
        return

    if hasattr(response, "data"):
        result = response.data
    else:
        try:
            result = json.loads(response.content)
        except Exception:  # pylint: disable=broad-except
            return
    if not isinstance(result, dict):
        return

    code = result.get("code", 0)
    try:
        code = int(code)
    except Exception:  # pylint: disable=broad-except
        pass
    if code in [0, "0", "00"]:
        span.set_status(Status(StatusCode.OK))
    else:
        span.set_status(Status(StatusCode.ERROR))

    span.set_attribute("result_code", code)
    span.set_attribute("result_message", result.get("message", ""))

    errors = result.get("errors", "")
    if errors:
        span.set_attribute("result_errors", errors)


class BKUserInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return []

    def _instrument(self, **kwargs):
        LoggingInstrumentor().instrument()
        print("otel instructment: logging")
        RequestsInstrumentor().instrument(span_callback=requests_callback)
        print("otel instructment: requests")
        DjangoInstrumentor().instrument(request_hook=django_request_hook, response_hook=django_response_hook)
        print("otel instructment: django")
        RedisInstrumentor().instrument()
        print("otel instructment: redis")

        if getattr(settings, "IS_USE_CELERY", False):
            from opentelemetry.instrumentation.celery import CeleryInstrumentor

            CeleryInstrumentor().instrument()
            print("otel instructment: celery")

        if getattr(settings, "OTEL_INSTRUMENT_DB_API", False):
            import MySQLdb  # noqa

            dbapi.wrap_connect(
                __name__,
                MySQLdb,
                "connect",
                "mysql",
                {"database": "db", "port": "port", "host": "host", "user": "user"},
            )
            print("otel instructment: database api")

    def _uninstrument(self, **kwargs):
        for instrumentor in self.instrumentors:
            print("otel uninstrument", instrumentor)
            instrumentor.uninstrument()