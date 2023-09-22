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
from typing import Any, Dict, Optional

from django.utils import timezone

from bkuser.apps.data_source.models import DataSource
from bkuser.apps.sync.constants import SyncTaskStatus
from bkuser.apps.sync.data_models import DataSourceSyncOptions, TenantSyncOptions
from bkuser.apps.sync.models import DataSourceSyncTask, TenantSyncTask
from bkuser.apps.sync.runners import DataSourceSyncTaskRunner, TenantSyncTaskRunner
from bkuser.apps.sync.tasks import sync_data_source, sync_tenant


class DataSourceSyncManager:
    """数据源同步管理器"""

    def __init__(self, data_source: DataSource, sync_options: DataSourceSyncOptions):
        self.data_source = data_source
        self.sync_options = sync_options

    def execute(self, context: Optional[Dict[str, Any]] = None) -> DataSourceSyncTask:
        """执行同步任务"""
        context = context or {}

        task = DataSourceSyncTask.objects.create(
            data_source_id=self.data_source.id,
            status=SyncTaskStatus.PENDING.value,
            trigger=self.sync_options.trigger,
            operator=self.sync_options.operator,
            start_at=timezone.now(),
            extra={
                "overwrite": self.sync_options.overwrite,
                "async_run": self.sync_options.async_run,
            },
        )

        if self.sync_options.async_run:
            self._ensure_only_basic_type_in_context(context)
            sync_data_source.delay(task.id, context)
        else:
            # 同步的方式，不需要序列化/反序列化，因此不需要检查基础类型
            DataSourceSyncTaskRunner(task, context).run()

        return task

    @staticmethod
    def _ensure_only_basic_type_in_context(context: Dict[str, Any]):
        """确保 context 中只有基础类型"""
        if not context:
            return

        for v in context.values():
            if isinstance(v, (int, float, str, bytes, bool, dict, list)):
                continue

            raise TypeError("only basic type allowed in context!")


class TenantSyncManager:
    """租户同步管理器"""

    def __init__(self, data_source: DataSource, tenant_id: str, sync_options: TenantSyncOptions):
        self.data_source = data_source
        self.tenant_id = tenant_id
        self.sync_options = sync_options

    def execute(self) -> TenantSyncTask:
        task = TenantSyncTask.objects.create(
            tenant_id=self.tenant_id,
            data_source_id=self.data_source.id,
            status=SyncTaskStatus.PENDING.value,
            trigger=self.sync_options.trigger,
            operator=self.sync_options.operator,
            start_at=timezone.now(),
            extra={"async_run": self.sync_options.async_run},
        )

        if self.sync_options.async_run:
            sync_tenant.delay(task.id)
        else:
            TenantSyncTaskRunner(task).run()

        return task
