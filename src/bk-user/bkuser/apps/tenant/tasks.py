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
from typing import List

from django.utils import timezone

from bkuser.apps.tenant.constants import NotificationScene
from bkuser.apps.tenant.models import Tenant, TenantUser, TenantUserValidityPeriodConfig
from bkuser.apps.tenant.notifier import TenantUserValidityPeriodNotifier
from bkuser.celery import app
from bkuser.common.task import BaseTask

logger = logging.getLogger(__name__)


@app.task(base=BaseTask, ignore_result=True)
def send_notifications(tenant_id: str, scene: NotificationScene, tenant_user_ids: List[str]):
    # TODO: 后续考虑租户、用户状态等，冻结等非正常状态用户不通知
    users = TenantUser.objects.filter(id__in=tenant_user_ids)
    logger.info(
        "going to send notification for users. user_count=%s tenant=%s, scene=%s", len(users), tenant_id, scene
    )
    try:
        TenantUserValidityPeriodNotifier(tenant_id=tenant_id, scene=scene).send(users)
    except Exception:
        logger.exception("send notification failed, please check!")


@app.task(base=BaseTask, ignore_result=True)
def notify_expiring_tenant_user():
    """扫描全部租户用户，做即将过期通知"""
    logger.info("[celery] receive period task:send_tenant_user_expiring_notification")
    now = timezone.now()

    # 获取账号有效期-临期配置
    tenant_remind_before_expire_list = TenantUserValidityPeriodConfig.objects.all().values(
        "tenant_id", "remind_before_expire"
    )

    for item in tenant_remind_before_expire_list:
        tenant_id, remind_before_expire = item["tenant_id"], item["remind_before_expire"]

        tenant_users = TenantUser.objects.filter(account_expired_at__date__gt=now.date(), tenant_id=tenant_id)

        # 临1/7/15天过期 条件设置, 每个租户的设置都不一样
        account_expired_date_list = []
        for remain_days in remind_before_expire:
            account_expired_at = now + datetime.timedelta(days=int(remain_days))
            account_expired_date_list.append(account_expired_at.date())

        should_notify_user_ids = list(
            tenant_users.filter(account_expired_at__date__in=account_expired_date_list).values_list("id", flat=True)
        )
        # 发送通知
        logger.info("going to notify expiring users in tenant{%s}, count: %s", tenant_id, len(should_notify_user_ids))

        if not should_notify_user_ids:
            continue

        send_notifications.delay(
            tenant_id=tenant_id, scene=NotificationScene.TENANT_USER_EXPIRING, tenant_user_ids=should_notify_user_ids
        )


@app.task(base=BaseTask, ignore_result=True)
def notify_expired_tenant_user():
    """扫描全部租户用户，做过期通知"""
    logger.info("[celery] receive period task:send_tenant_user_expired_notification")

    # 今日过期, 当前时间转换为实际时区的时间
    now = timezone.now()

    # 获取 租户-过期用户
    tenant_ids = Tenant.objects.all().values_list("id", flat=True)

    for tenant_id in tenant_ids:
        # 发送过期通知
        should_notify_user_ids = list(
            TenantUser.objects.filter(
                account_expired_at__date=now.date(),
                tenant_id=tenant_id,
            ).values_list("id", flat=True)
        )

        logger.info("going to notify expired users in tenant{%s}, count: %s", tenant_id, len(should_notify_user_ids))
        if not should_notify_user_ids:
            continue

        send_notifications.delay(
            tenant_id=tenant_id, scene=NotificationScene.TENANT_USER_EXPIRED, tenant_user_ids=should_notify_user_ids
        )
