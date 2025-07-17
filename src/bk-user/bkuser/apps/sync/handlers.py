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
import json
import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask
from pydantic import ValidationError

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.sync.constants import DataSourceSyncPeriodType
from bkuser.apps.sync.data_models import DataSourceSyncConfig, TenantSyncOptions
from bkuser.apps.sync.managers import TenantSyncManager
from bkuser.apps.sync.names import gen_data_source_sync_periodic_task_name
from bkuser.apps.sync.signals import post_sync_data_source, post_sync_tenant
from bkuser.apps.sync.tasks import initialize_identity_info_and_send_notification
from bkuser.apps.tenant.constants import CollaborationStrategyStatus
from bkuser.apps.tenant.models import CollaborationStrategy

logger = logging.getLogger(__name__)


@receiver(post_sync_data_source)
def sync_tenant_departments_users(sender, data_source: DataSource, **kwargs):
    """同步租户数据（部门 & 用户）"""
    sync_opts = TenantSyncOptions()
    # 同步到数据源所属租户
    TenantSyncManager(data_source, data_source.owner_tenant_id, sync_opts).execute()

    # 虽然逻辑上只有实名数据源会同步 & 发送 post_sync_data_source 信号，但是防御一下比较好
    if data_source.type != DataSourceTypeEnum.REAL:
        logger.warning("data source %s is not real user type, skip sync...", data_source.id)
        return

    # 根据配置的协同策略，同步其他租户
    for strategy in CollaborationStrategy.objects.filter(source_tenant_id=data_source.owner_tenant_id):
        # 任意一方状态不是已启用，就不会执行协同同步
        if strategy.source_status != CollaborationStrategyStatus.ENABLED:
            logger.info("collaboration strategy %s is not enabled by source, skip sync...", strategy.id)
            continue
        if strategy.target_status != CollaborationStrategyStatus.ENABLED:
            logger.info("collaboration strategy %s is not enabled by target, skip sync...", strategy.id)
            continue

        TenantSyncManager(data_source, strategy.target_tenant_id, sync_opts).execute()


@receiver(post_sync_tenant)
def sync_identity_infos_and_notify_after_sync_tenant(sender, data_source: DataSource, **kwargs):
    """
    在完成租户同步后，需要对本地数据源的用户账密信息做初始化

    Q: 为什么在完成租户同步后才初始化本地数据源用户账密信息（而不是数据源同步后就整）?
    A: 1. 初始化后，通知只能发送给租户用户，因此需要等待租户同步完成后才执行
       2. 用户管理对外只有租户用户，如果租户用户未创建，则初始化也是没有意义的
    """
    transaction.on_commit(lambda: initialize_identity_info_and_send_notification.delay(data_source.id))


@receiver(post_save, sender=DataSource)
def sync_identity_infos_and_notify_after_modify_data_source(sender, instance: DataSource, created: bool, **kwargs):
    """
    数据源更新后，需要检查是否是本地数据源，若是本地数据源且启用密码功能，
    则需要对没有账密信息的用户，进行密码的初始化 & 发送通知，批量创建数据源用户同理
    """
    if created:
        # 数据源刚刚创建的信号不需要处理，因为此时没有数据源用户 & 租户用户
        return

    transaction.on_commit(lambda: initialize_identity_info_and_send_notification.delay(instance.id))


def gen_data_source_sync_periodic_task_name_with_time(data_source_id: int, time_index: str = "") -> str:
    """生成带索引后缀的数据源同步任务名称"""
    # 若固定时间点数量为 1，则不生成索引后缀，使用默认任务名
    base_name = gen_data_source_sync_periodic_task_name(data_source_id)
    return f"{base_name}_{time_index}" if time_index else base_name


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
        PeriodicTask.objects.filter(name__startswith=periodic_task_name).delete()
        return

    try:
        cfg = DataSourceSyncConfig(**data_source.sync_config)
    except ValidationError:
        logger.exception("data source %s sync_config invalid, skip set sync periodic task", data_source.id)
        return

    # sync_period 为 Never 时，表示当前数据源数据不会定时同步，只能通过手动同步
    if cfg.period_type == DataSourceSyncPeriodType.NEVER:
        logger.info(
            "data source %s has period_type -> never. Any existing periodic tasks will be removed.",
            data_source.id,
        )
        PeriodicTask.objects.filter(name__startswith=periodic_task_name).delete()
        return

    # 在事务中处理任务的创建和删除，避免并发修改
    with transaction.atomic():
        sync_periodic_tasks_for_data_source(data_source, cfg)


def sync_periodic_tasks_for_data_source(data_source: DataSource, cfg: DataSourceSyncConfig):
    """
    同步数据源的定时任务

    - 分钟级别：使用IntervalSchedule，每隔 N 分钟触发一次
    - 小时级别：使用CrontabSchedule，每 N 小时在指定分钟触发
    - 天级别：使用CrontabSchedule，每 N 天在指定时间触发
    """
    base_task_name = gen_data_source_sync_periodic_task_name(data_source.id)

    try:
        # 在事务中使用 select_for_update 锁定相关的 PeriodicTask，避免并发修改
        tasks_to_delete = PeriodicTask.objects.select_for_update().filter(name__startswith=base_task_name)
        tasks_to_delete.delete()

        # 根据配置类型创建新任务
        if cfg.period_type == DataSourceSyncPeriodType.MINUTE:
            _create_interval_task(data_source, cfg, base_task_name)
        else:
            _create_crontab_tasks(data_source, cfg)

    except Exception:
        logger.exception("Failed to sync periodic tasks for data source %s", data_source.id)


def _create_interval_task(data_source: DataSource, cfg: DataSourceSyncConfig, task_name: str):
    """创建 interval 任务（分钟级别）"""
    interval_schedule = cfg.get_interval_schedule()

    PeriodicTask.objects.update_or_create(
        name=task_name,
        defaults={
            "interval": interval_schedule,
            "task": "bkuser.apps.sync.periodic_tasks.build_and_run_data_source_sync_task",
            "kwargs": json.dumps({"data_source_id": data_source.id}),
        },
    )

    logger.info(
        "created/updated data source %s sync periodic task: %s with interval %s minutes",
        data_source.id,
        task_name,
        cfg.period_value,
    )


def _create_crontab_tasks(data_source: DataSource, cfg: DataSourceSyncConfig):
    """创建 crontab 任务（小时/天级别）"""
    crontab_schedules = cfg.get_crontab_schedules()

    for i, schedule in enumerate(crontab_schedules):
        # 为每个固定时间点生成唯一的任务名，用于区分多个执行时间点的任务
        if len(crontab_schedules) > 1:
            time_suffix = f"time_{i+1}"
        else:
            time_suffix = ""

        task_name = gen_data_source_sync_periodic_task_name_with_time(data_source.id, time_suffix)

        PeriodicTask.objects.update_or_create(
            name=task_name,
            defaults={
                "crontab": schedule,
                "task": "bkuser.apps.sync.periodic_tasks.build_and_run_data_source_sync_task",
                "kwargs": json.dumps(
                    {
                        "data_source_id": data_source.id,
                        "exec_time_index": i,
                    }
                ),
            },
        )

        logger.info(
            "created/updated data source %s sync periodic task: %s with crontab %s %s %s %s %s",
            data_source.id,
            task_name,
            schedule.minute,
            schedule.hour,
            schedule.day_of_week,
            schedule.day_of_month,
            schedule.month_of_year,
        )
