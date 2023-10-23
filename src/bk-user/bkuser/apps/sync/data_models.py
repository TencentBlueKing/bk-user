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
from pydantic import BaseModel

from bkuser.apps.sync.constants import DataSourceSyncPeriod, SyncTaskTrigger


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

    sync_period: DataSourceSyncPeriod = DataSourceSyncPeriod.PER_1_DAY
