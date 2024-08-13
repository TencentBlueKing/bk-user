# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.core.management.base import BaseCommand

from bkuser.apps.sync.constants import DATA_SOURCE_SYNC_DEFAULT_TIMEOUT
from bkuser.apps.sync.locks import DataSourceSyncTaskLock, TenantSyncTaskLock
from bkuser.apps.sync.models import DataSourceSyncTask, TenantSyncTask


class LockType(str, StructuredEnum):
    DATA_SOURCE_SYNC = EnumField("data_source_sync")
    TENANT_SYNC = EnumField("tenant_sync")


class Command(BaseCommand):
    """
    强制释放数据源同步 / 租户同步锁

    - 释放数据源同步锁
    $ python manage.py release_sync_lock --type data_source_sync --task 1

    - 释放租户同步锁
    $ python manage.py release_sync_lock --type tenant_sync --task 1

    注意：释放锁并不会中断正在运行的任务，需要小心并发同步导致的数据问题
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--type", dest="lock_type", required=True, help="锁类型，可选项：data_source_sync, tenant_sync"
        )
        parser.add_argument("--task", dest="task_id", required=True, help="数据源 / 租户同步任务 ID")

    def handle(self, lock_type: LockType, task_id: int, *args, **options):
        if lock_type == LockType.DATA_SOURCE_SYNC:
            self._release_data_source_sync_lock(task_id)
        elif lock_type == LockType.TENANT_SYNC:
            self._release_tenant_sync_lock(task_id)
        else:
            raise ValueError(f"invalid lock type: {lock_type.value}")

        self.stdout.write("lock release success!")

    def _release_data_source_sync_lock(self, task_id: int):
        """释放数据源同步锁"""
        task = DataSourceSyncTask.objects.filter(id=task_id).first()
        if not task:
            raise RuntimeError(f"data source sync task {task_id} not found!")

        DataSourceSyncTaskLock(task.data_source_id, DATA_SOURCE_SYNC_DEFAULT_TIMEOUT).release()

    def _release_tenant_sync_lock(self, task_id: int):
        """释放租户同步锁"""
        task = TenantSyncTask.objects.filter(id=task_id).first()
        if not task:
            raise RuntimeError(f"tenant sync task {task_id} not found!")

        TenantSyncTaskLock(task.tenant_id, task.data_source_id).release()
