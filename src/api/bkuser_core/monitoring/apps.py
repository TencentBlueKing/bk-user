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
from celery.signals import worker_process_init
from django.apps import AppConfig

from bkuser_global.tracing.otel import setup_by_settings
from bkuser_global.tracing.sentry import init_sentry_sdk


class MonitoringConfig(AppConfig):
    name = "bkuser_core.monitoring"

    def ready(self):
        setup_by_settings()
        init_sentry_sdk("bk-user-api", django_integrated=True, redis_integrated=True, celery_integrated=True)


@worker_process_init.connect(weak=False)
def worker_process_init_otel_trace_setup(*args, **kwargs):
    setup_by_settings()


@worker_process_init.connect(weak=False)
def worker_process_init_sentry_setup(*args, **kwargs):
    init_sentry_sdk("bk-user-api")
