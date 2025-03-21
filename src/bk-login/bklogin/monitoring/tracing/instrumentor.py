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

import logging
from typing import Collection

from django.conf import settings
from opentelemetry.instrumentation import dbapi
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor  # type: ignore
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from .hooks import django_request_hook, django_response_hook, requests_response_hook

logger = logging.getLogger(__name__)


class BKLoginInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return []

    def _instrument(self, **kwargs):
        LoggingInstrumentor().instrument()
        logger.info("otel instructment: logging")
        RequestsInstrumentor().instrument(response_hook=requests_response_hook)
        logger.info("otel instructment: requests")
        DjangoInstrumentor().instrument(request_hook=django_request_hook, response_hook=django_response_hook)
        logger.info("otel instructment: django")

        if getattr(settings, "OTEL_INSTRUMENT_DB_API", False):
            import pymysql

            dbapi.wrap_connect(
                __name__,
                pymysql.connect,
                "connect",
                "mysql",
                {"database": "db", "port": "port", "host": "host", "user": "user"},
            )
            logger.info("otel instructment: database api")

    def _uninstrument(self, **kwargs):
        for instrumentor in self.instrumentors:
            logger.info("otel uninstrument %s", instrumentor)
            instrumentor.uninstrument()
