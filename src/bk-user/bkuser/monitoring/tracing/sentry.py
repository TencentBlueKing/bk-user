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
from typing import List

import sentry_sdk
from sentry_sdk.integrations import Integration


def init_sentry_sdk(django_integrated: bool = True, redis_integrated: bool = False, celery_integrated: bool = False):
    """Register celery error events to sentry"""
    from django.conf import settings

    integrations: List[Integration] = []
    if django_integrated:
        from sentry_sdk.integrations.django import DjangoIntegration

        integrations.append(DjangoIntegration())

    if redis_integrated:
        from sentry_sdk.integrations.redis import RedisIntegration

        integrations.append(RedisIntegration())

    if celery_integrated:
        from sentry_sdk.integrations.celery import CeleryIntegration

        integrations.append(CeleryIntegration())

    if settings.SENTRY_DSN:
        # 初始化 sentry_sdk
        sentry_sdk.init(  # type: ignore
            # debug=True,
            dsn=settings.SENTRY_DSN,
            integrations=integrations,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production,
            traces_sample_rate=1.0,
            # If you wish to associate users to errors (assuming you are using
            # django.contrib.auth) you may enable sending PII data.
            send_default_pii=True,
            # By default, the SDK will try to use the SENTRY_RELEASE
            # environment variable, or infer a git commit
            # SHA as release, however you may want to set
            # something more human-readable.
            # release="myapp@1.0.0",
            # Can export the environment
            # environment="production",
        )
