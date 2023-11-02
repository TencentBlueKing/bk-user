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
import json
import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from pydantic import ValidationError

from bkuser.apps.data_source.models import DataSource
from bkuser.apps.data_source.tasks import initialize_identity_info_and_send_notification
from bkuser.apps.sync.constants import DataSourceSyncPeriod
from bkuser.apps.sync.data_models import DataSourceSyncConfig, TenantSyncOptions
from bkuser.apps.sync.managers import TenantSyncManager
from bkuser.apps.sync.names import gen_data_source_sync_periodic_task_name
from bkuser.apps.sync.signals import post_sync_data_source

logger = logging.getLogger(__name__)


@receiver(post_sync_data_source)
def sync_identity_infos_and_notify(sender, data_source: DataSource, **kwargs):
    """在完成数据源同步后，需要对本地数据源的用户账密信息做初始化"""
    transaction.on_commit(lambda: initialize_identity_info_and_send_notification.delay(data_source.id))


@receiver(post_sync_data_source)
def sync_tenant_departments_users(sender, data_source: DataSource, **kwargs):
    """同步租户数据（部门 & 用户）"""
    # TODO (su) 目前没有跨租户协同，因此只要往数据源所属租户同步即可
    TenantSyncManager(data_source, data_source.owner_tenant_id, TenantSyncOptions()).execute()


@receiver(post_save, sender=DataSource)
def set_data_source_sync_periodic_task(sender, instance: DataSource, **kwargs):
    """在创建/修改数据源后，需要设置定时同步的任务"""
    data_source = instance
    if data_source.is_local:
        logger.info("skip set sync periodic task for local data source %s", data_source.id)
        return

    periodic_task_name = gen_data_source_sync_periodic_task_name(data_source.id)
    # 没有同步配置，抛出 warning 并且跳过
    if not data_source.sync_config:
        logger.warning("data source %s hasn't sync_config, remove sync periodic task...", data_source.id)
        PeriodicTask.objects.filter(name=periodic_task_name).delete()
        return

    try:
        cfg = DataSourceSyncConfig(**data_source.sync_config)
    except ValidationError:
        logger.exception("data source %s sync_config invalid, skip set sync periodic task", data_source.id)
        return

    # sync_period 为 Never 时，表示当前数据源数据不会定时同步，只能通过手动同步
    if cfg.sync_period == DataSourceSyncPeriod.NEVER:
        logger.info(
            "data source %s has sync_period -> never (0). Any existing periodic tasks will be removed.",
            data_source.id,
        )
        PeriodicTask.objects.filter(name=periodic_task_name).delete()
        return

    interval_schedule, _ = IntervalSchedule.objects.get_or_create(
        every=cfg.sync_period,
        period=IntervalSchedule.MINUTES,
    )
    periodic_task, task_created = PeriodicTask.objects.get_or_create(
        name=periodic_task_name,
        defaults={
            "interval": interval_schedule,
            "task": "bkuser.apps.sync.periodic_tasks.build_and_run_data_source_sync_task",
            "kwargs": json.dumps({"data_source_id": data_source.id}),
        },
    )
    if not task_created:
        logger.info(
            "update data source %s sync periodic task's period as %s",
            data_source.id,
            cfg.sync_period,
        )
        periodic_task.interval = interval_schedule
        periodic_task.save()
