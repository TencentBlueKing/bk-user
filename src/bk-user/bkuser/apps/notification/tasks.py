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
import logging
from datetime import timedelta
from functools import reduce

from django.db.models import Q
from django.utils import timezone

from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.notification.constants import NotificationScene
from bkuser.apps.notification.notifier import TenantUserNotifier
from bkuser.apps.tenant.models import Tenant, TenantUser, TenantUserValidityPeriodConfig
from bkuser.celery import app
from bkuser.common.task import BaseTask

logger = logging.getLogger(__name__)


@app.task(base=BaseTask, ignore_result=True)
def send_reset_password_to_user(data_source_user_id: int, new_password: str):
    """发送被重置的新密码通知到用户"""
    data_source_user = DataSourceUser.objects.select_related("data_source").get(id=data_source_user_id)
    tenant_user = TenantUser.objects.get(
        data_source_user=data_source_user, tenant_id=data_source_user.data_source.owner_tenant_id
    )
    TenantUserNotifier(NotificationScene.MANAGER_RESET_PASSWORD).send(tenant_user, passwd=new_password)


# TODO (su) 密码即将过期/已过期也需要对应的通知任务


@app.task(base=BaseTask, ignore_result=True)
def notify_expiring_tenant_users(tenant_id: str):
    """对即将过期的租户用户发送通知"""
    logger.info("[celery] receive task: notify_expiring_tenant_users, tenant_id is %s", tenant_id)

    time_now = timezone.now()
    cfg = TenantUserValidityPeriodConfig.objects.get(tenant_id=tenant_id)
    if not cfg.remind_before_expire:
        logger.warning("tenant %s didn't set remind before expire config, skip notify...", tenant_id)
        return

    tenant_users = TenantUser.objects.filter(tenant_id=tenant_id)

    # 将要过期提醒，支持配置多值，对应 1/7/15 天等
    expired_date_filters = []
    for remain_days in cfg.remind_before_expire:
        expired_at = time_now + timedelta(days=int(remain_days))
        expired_date_filters.append(
            Q(account_expired_at__gt=expired_at - timedelta(1), account_expired_at__lte=expired_at)
        )

    tenant_users = tenant_users.filter(reduce(lambda x, y: x | y, expired_date_filters))
    if not tenant_users.exists():
        logger.info("tenant %s not tenant user need expiring notification, skip notify...", tenant_id)
        return

    logger.info("tenant %s send expiring notification to %d users...", tenant_id, tenant_users.count())
    TenantUserNotifier(NotificationScene.TENANT_USER_EXPIRING, tenant_id=tenant_id).batch_send(tenant_users)


@app.task(base=BaseTask, ignore_result=True)
def build_and_run_notify_expiring_tenant_users_task():
    """构建并运行即将过期通知任务"""
    logger.info("[celery] receive period task: build_and_run_notify_expiring_tenant_users_task")

    for tenant_id in Tenant.objects.all().values_list("id", flat=True):
        notify_expiring_tenant_users.delay(tenant_id)


@app.task(base=BaseTask, ignore_result=True)
def notify_expired_tenant_users(tenant_id: str):
    """对当天过期的租户用户发送通知"""
    logger.info("[celery] receive task: notify_expired_tenant_users, tenant_id is %s", tenant_id)

    time_now = timezone.now()
    # Q：为什么不使用 account_expired_at__date=time_now.date() 的方式？
    # A：在 USE_TZ == True 的情况下，查询的 SQL 中会使用 CONVERT_TZ 对时间进行转换，
    #    该转换要求 DB 中有配置对应的时区（如 UTC，GMT，Asia/Shanghai 等）
    #    但是 MySQL 中默认是只有 SYSTEM 时区的，转换会失败（NULL），导致查询不到任何有效值
    #    ref: https://docs.djangoproject.com/en/dev/ref/models/querysets/#date
    tenant_users = TenantUser.objects.filter(
        tenant_id=tenant_id, account_expired_at__gt=time_now - timedelta(1), account_expired_at__lte=time_now
    )
    if not tenant_users.exists():
        logger.info("tenant %s not tenant user expired today, skip notify...", tenant_id)
        return

    logger.info("tenant %s send expired notification to %d users...", tenant_id, tenant_users.count())
    TenantUserNotifier(NotificationScene.TENANT_USER_EXPIRED, tenant_id=tenant_id).batch_send(tenant_users)


@app.task(base=BaseTask, ignore_result=True)
def build_and_run_notify_expired_tenant_users_task():
    """构建并运行过期通知任务"""
    logger.info("[celery] receive period task: build_and_run_notify_expired_tenant_users_task")

    for tenant_id in Tenant.objects.all().values_list("id", flat=True):
        notify_expired_tenant_users.delay(tenant_id)
