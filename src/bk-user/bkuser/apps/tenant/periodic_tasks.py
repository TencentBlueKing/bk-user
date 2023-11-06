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
import datetime
import logging

from django.utils import timezone

from bkuser.apps.tenant.constants import NotificationScene
from bkuser.apps.tenant.models import Tenant, TenantUser, TenantUserValidityPeriodConfig
from bkuser.apps.tenant.notifier import TenantUserValidityPeriodNotifier
from bkuser.celery import app
from bkuser.common.task import BaseTask

logger = logging.getLogger(__name__)


@app.task(base=BaseTask, ignore_result=True)
def send_tenant_user_expiring_notification():
    """扫描全部租户用户，做临期通知"""
    logger.info("[celery] receive period task:send_tenant_user_expiring_notification")
    now = timezone.now()

    # 获取 租户-未过期用户 映射
    tenant_ids = Tenant.objects.filter().values_list("id", flat=True)
    tenant_users_map = {
        tenant_id: TenantUser.objects.filter(account_expired_at__gt=now.date(), tenant_id=tenant_id)
        for tenant_id in tenant_ids
    }

    # 获取账号有效期-临期配置
    tenant_remind_before_expire_map = {
        tenant_id: TenantUserValidityPeriodConfig.objects.filter(tenant_id=tenant_id).first().remind_before_expire
        for tenant_id in tenant_ids
    }

    for tenant_id, remind_before_expire in tenant_remind_before_expire_map.items():
        tenant_users = tenant_users_map[tenant_id]

        # 临1/7/15天过期 条件设置, 每个租户的设置都不一样
        account_expired_at_conditions = [
            now.date() + datetime.timedelta(days=int(remain_days)) for remain_days in remind_before_expire
        ]
        should_notify_users = list(tenant_users.filter(account_expired_at__in=account_expired_at_conditions))
        # 发送通知
        logger.info("going to notify expiring users in tenant-%s, count: %s", tenant_id, len(should_notify_users))

        TenantUserValidityPeriodNotifier(tenant_id=tenant_id, scene=NotificationScene.TENANT_USER_EXPIRING).send(
            should_notify_users
        )


@app.task(base=BaseTask, ignore_result=True)
def send_tenant_user_expired_notification():
    """扫描全部租户用户，做过期通知"""
    logger.info("[celery] receive period task:send_tenant_user_expired_notification")

    # 今日过期
    now_date = timezone.now().date()

    # 获取 租户-过期用户
    tenant_ids = Tenant.objects.filter().values_list("id", flat=True)
    tenant_user_map = {
        tenant_id: TenantUser.objects.filter(account_expired_at=now_date, tenant_id=tenant_id)
        for tenant_id in tenant_ids
    }

    for tenant_id, tenant_users in tenant_user_map.items():
        # 发送通知 过期
        logger.info("going to notify expired users in tenant-%s, count: %s", tenant_id, len(tenant_users))

        TenantUserValidityPeriodNotifier(tenant_id=tenant_id, scene=NotificationScene.TENANT_USER_EXPIRED).send(
            list(tenant_users)
        )
