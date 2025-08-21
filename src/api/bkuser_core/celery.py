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
import os
import environ
from celery import Celery
env = environ.Env()

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bkuser_core.config.overlays.prod")

app = Celery("bkuser_core")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.update(
    broker_transport_options={
        'visibility_timeout': 3600,
        'fanout_prefix': True,
        'master_name': env("CACHE_REDIS_SENTINEL_MASTER_NAME", default="bk-redis-master-0"),
        'socket_timeout': 5,
        'retry_policy': {
            'interval_start': 0,
            'interval_step': 0.2,
            'max_retries': 3,
        }
    },
    task_acks_late=True,
    task_reject_on_worker_lost=True
)
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
app.autodiscover_tasks(related_name="extra_tasks")
