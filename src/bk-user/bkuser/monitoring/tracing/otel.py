# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import threading

from django.conf import settings
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import _KNOWN_SAMPLERS

from .instrumentor import BKUserInstrumentor


class LazyBatchSpanProcessor(BatchSpanProcessor):
    def __init__(self, *args, **kwargs):
        super(LazyBatchSpanProcessor, self).__init__(*args, **kwargs)
        # 停止默认线程
        self.done = True
        with self.condition:
            self.condition.notify_all()
        self.worker_thread.join()  # type: ignore
        self.done = False
        self.worker_thread = None  # type: ignore

    def on_end(self, span: ReadableSpan) -> None:
        if self.worker_thread is None:
            self.worker_thread = threading.Thread(name=self.__class__.__name__, target=self.worker, daemon=True)
            self.worker_thread.start()
        super(LazyBatchSpanProcessor, self).on_end(span)

    def shutdown(self) -> None:
        # signal the worker thread to finish and then wait for it
        self.done = True
        with self.condition:
            self.condition.notify_all()
        if self.worker_thread:
            self.worker_thread.join()
        self.span_exporter.shutdown()


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
