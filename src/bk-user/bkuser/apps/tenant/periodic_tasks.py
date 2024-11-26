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
from datetime import timedelta

from django.utils import timezone

from bkuser.apps.tenant.constants import TenantUserStatus
from bkuser.apps.tenant.models import TenantUser
from bkuser.celery import app
from bkuser.common.task import BaseTask
from bkuser.utils.time import get_midnight

logger = logging.getLogger(__name__)


@app.task(base=BaseTask, ignore_result=True)
def update_expired_tenant_user_status():
    """定时任务：更新昨日过期用户的状态"""
    logger.info("[celery] receive task: update_expired_tenant_user_status")

    midnight = get_midnight()

    expired_users = TenantUser.objects.filter(
        status=TenantUserStatus.ENABLED,
        account_expired_at__gte=midnight - timedelta(days=1),
        account_expired_at__lt=midnight,
    )

    if not expired_users.exists():
        logger.info("No expired users found.")
        return

    expired_count = expired_users.update(status=TenantUserStatus.EXPIRED, updated_at=timezone.now())
    logger.info("Update %d expired users to EXPIRED status.", expired_count)
