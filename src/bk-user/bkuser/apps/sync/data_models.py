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
from datetime import time

from django.conf import settings
from django_celery_beat.models import IntervalSchedule
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
    exec_time: time | None = None
    sync_timeout: int = settings.DATA_SOURCE_SYNC_DEFAULT_TIMEOUT

    def get_interval_schedule(self):
        """根据配置生成 IntervalSchedule"""
        if self.period_type == DataSourceSyncPeriodType.MINUTE:
            return IntervalSchedule.objects.get_or_create(
                every=self.period_value,
                period=IntervalSchedule.MINUTES,
            )
        if self.period_type == DataSourceSyncPeriodType.HOUR:
            return IntervalSchedule.objects.get_or_create(
                every=self.period_value,
                period=IntervalSchedule.HOURS,
            )
        if self.period_type == DataSourceSyncPeriodType.DAY:
            return IntervalSchedule.objects.get_or_create(
                every=self.period_value,
                period=IntervalSchedule.DAYS,
            )
        raise ValueError(f"Unsupported period_type: {self.period_type}")
