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
import threading
from typing import Optional

from django.conf import settings
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, Span, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter
from opentelemetry.sdk.trace.sampling import _KNOWN_SAMPLERS

from .instrumentor import BKUserInstrumentor


class LazyBatchSpanProcessor:
    def __init__(self, span_exporter: SpanExporter, **kwargs):
        self._span_exporter = span_exporter
        self._kwargs = kwargs
        self._inner: Optional[BatchSpanProcessor] = None
        self._lock = threading.Lock()
        self._started = False

    def _ensure_started(self):
        if not self._started:
            with self._lock:
                if not self._started:
                    self._inner = BatchSpanProcessor(self._span_exporter, **self._kwargs)

    def on_start(self, span: Span, parent_context=None):
        self._ensure_started()
        if self._inner:
            self._inner.on_start(span, parent_context)

    def on_end(self, span: ReadableSpan) -> None:
        if not span.context.trace_flags.sampled:
            return
        self._ensure_started()
        if self._inner:
            self._inner.on_end(span)

    def shutdown(self) -> None:
        if self._inner:
            self._inner.shutdown()

    def force_flush(self, timeout_millis: Optional[int] = None) -> bool:
        if self._inner:
            return self._inner.force_flush(timeout_millis)
        return True


def setup_trace_config():
    # 注：测试用的 jaeger 也是直接使用 otlp_exporter 即可
    # pypi ref: https://pypi.org/project/opentelemetry-exporter-jaeger/
    # Since v1.35, the Jaeger supports OTLP natively. Please use the OTLP exporter instead.
    trace.set_tracer_provider(
        tracer_provider=TracerProvider(
            resource=Resource.create(
                {
                    "service.name": settings.OTEL_SERVICE_NAME,
                    "bk.data.token": settings.OTEL_DATA_TOKEN,
                },
            ),
            sampler=_KNOWN_SAMPLERS[settings.OTEL_SAMPLER],  # type: ignore
        )
    )
    otlp_exporter = OTLPSpanExporter(endpoint=settings.OTEL_GRPC_URL, insecure=True)
    span_processor = LazyBatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)  # type: ignore


def setup_by_settings():
    if not settings.ENABLE_OTEL_TRACE:
        return

    setup_trace_config()
    BKUserInstrumentor().instrument()
