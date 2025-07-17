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
from datetime import datetime
from typing import List

from django.conf import settings
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, IntervalSchedule
from pydantic import BaseModel

from bkuser.apps.sync.constants import DataSourceSyncPeriodType, SyncTaskTrigger


class DataSourceSyncOptions(BaseModel):
    """数据源同步选项"""

    # 同步操作人，定时触发时为空
    operator: str = ""
    # 是否对同名用户覆盖更新
    overwrite: bool = False
    # 是否使用增量同步
    incremental: bool = False
    # 是否异步执行同步任务
    async_run: bool = True
    # 同步任务触发方式
    trigger: SyncTaskTrigger = SyncTaskTrigger.CRONTAB


class TenantSyncOptions(BaseModel):
    """租户同步选项"""

    # 同步操作人，定时触发时为空
    operator: str = ""
    # 是否异步执行同步任务
    async_run: bool = True
    # 同步任务触发方式
    trigger: SyncTaskTrigger = SyncTaskTrigger.SIGNAL


class DataSourceSyncConfig(BaseModel):
    """数据源同步配置"""

    period_type: DataSourceSyncPeriodType = DataSourceSyncPeriodType.MINUTE
    period_value: int = 24 * 60
    exec_times: List[datetime] = []
    sync_timeout: int = settings.DATA_SOURCE_SYNC_DEFAULT_TIMEOUT

    def get_interval_schedule(self) -> IntervalSchedule:
        """为分钟类型生成 IntervalSchedule"""
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=self.period_value,
            period=IntervalSchedule.MINUTES,
        )
        return schedule

    def get_crontab_schedules(self) -> List[CrontabSchedule]:
        """根据配置生成 CrontabSchedule 列表"""
        schedules: List[CrontabSchedule] = []

        if self.period_type == DataSourceSyncPeriodType.HOUR:
            # 小时级别：每小时在指定分钟触发，间隔检查在任务执行时进行
            for exec_time in self.exec_times:
                # 转换为本地时区来获取正确的小时和分钟
                local_time = timezone.localtime(exec_time)
                schedule, _ = CrontabSchedule.objects.get_or_create(
                    minute=str(local_time.minute),
                    hour="*",
                    day_of_week="*",
                    day_of_month="*",
                    month_of_year="*",
                    timezone=settings.TIME_ZONE,
                )
                schedules.append(schedule)

        elif self.period_type == DataSourceSyncPeriodType.DAY:
            # 天级别：每天在指定时间触发，间隔检查在任务执行时进行
            for exec_time in self.exec_times:
                # 转换为本地时区来获取正确的小时和分钟
                local_time = timezone.localtime(exec_time)
                schedule, _ = CrontabSchedule.objects.get_or_create(
                    minute=str(local_time.minute),
                    hour=str(local_time.hour),
                    day_of_week="*",
                    day_of_month="*",
                    month_of_year="*",
                    timezone=settings.TIME_ZONE,
                )
                schedules.append(schedule)

        return schedules

    def should_execute_now(self, exec_time: datetime) -> bool:
        """
        判断现在是否应该执行任务
        """
        now = timezone.now()

        if self.period_value == 1:
            # period_value = 1 时，由 crontab 精确控制，无需判断
            return True

        if self.period_type == DataSourceSyncPeriodType.MINUTE:
            # 分钟级别：由 IntervalSchedule 控制间隔，直接执行
            return True

        if self.period_type == DataSourceSyncPeriodType.HOUR:
            # 小时级别：检查距离参考时间的小时数是否为间隔的倍数
            now_local = timezone.localtime(now)
            exec_time_local = timezone.localtime(exec_time)

            # 计算总的小时差，考虑跨天的情况
            time_delta = now_local - exec_time_local
            hour_delta = time_delta.days * 24 + time_delta.seconds // 3600
            return hour_delta % self.period_value == 0

        if self.period_type == DataSourceSyncPeriodType.DAY:
            # 天级别：检查距离参考时间的天数是否为间隔的倍数
            # 使用本地时区的日期来计算，避免UTC时区差异导致的日期偏移
            now_local = timezone.localtime(now)
            exec_time_local = timezone.localtime(exec_time)
            days_delta = (now_local.date() - exec_time_local.date()).days
            return days_delta % self.period_value == 0

        return True
