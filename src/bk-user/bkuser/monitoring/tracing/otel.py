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

from django.conf import settings
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._shared_internal import BatchProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter
from opentelemetry.sdk.trace.sampling import _KNOWN_SAMPLERS

from .instrumentor import BKUserInstrumentor


class LazyBatchSpanProcessor(BatchSpanProcessor):
    def __init__(
        self,
        span_exporter: SpanExporter,
        max_queue_size: int | None = None,
        schedule_delay_millis: float | None = None,
        max_export_batch_size: int | None = None,
        export_timeout_millis: float | None = None,
    ):
        self._span_exporter = span_exporter
        self._max_queue_size = (
            max_queue_size if max_queue_size is not None else BatchSpanProcessor._default_max_queue_size()
        )
        self._schedule_delay_millis = (
            schedule_delay_millis
            if schedule_delay_millis is not None
            else BatchSpanProcessor._default_schedule_delay_millis()
        )
        self._max_export_batch_size = (
            max_export_batch_size
            if max_export_batch_size is not None
            else BatchSpanProcessor._default_max_export_batch_size()
        )
        self._export_timeout_millis = (
            export_timeout_millis
            if export_timeout_millis is not None
            else BatchSpanProcessor._default_export_timeout_millis()
        )
        self._batch_processor_initialized = False
        self._inner_batch_processor: BatchProcessor | None = None
        self._lock = threading.Lock()
        BatchSpanProcessor._validate_arguments(
            self._max_queue_size, self._schedule_delay_millis, self._max_export_batch_size
        )

    @property  # type: ignore[override]
    def _batch_processor(self) -> BatchProcessor:
        # Double check
        if not self._batch_processor_initialized:
            with self._lock:
                if not self._batch_processor_initialized:
                    self._inner_batch_processor = BatchProcessor(
                        exporter=self._span_exporter,
                        schedule_delay_millis=self._schedule_delay_millis,
                        max_export_batch_size=self._max_export_batch_size,
                        export_timeout_millis=self._export_timeout_millis,
                        max_queue_size=self._max_queue_size,
                        exporting="Span",
                    )
                    self._batch_processor_initialized = True
        return self._inner_batch_processor  # type: ignore[return-value]


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
