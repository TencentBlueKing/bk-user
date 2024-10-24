# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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

# ignore custom logger must use %s string format in this file
# ruff: noqa: G003, G004
import logging
import traceback
from typing import List

from celery.exceptions import SoftTimeLimitExceeded
from django.utils import timezone

from bkuser.apps.sync.constants import SyncOperation, SyncTaskStatus, TenantSyncObjectType
from bkuser.apps.sync.exceptions import TenantSyncInterrupted
from bkuser.apps.sync.locks import TenantSyncTaskLock
from bkuser.apps.sync.loggers import TaskLogger
from bkuser.apps.sync.models import TenantDepartmentChangeLog, TenantSyncTask, TenantUserChangeLog
from bkuser.apps.sync.recorders import ChangeLogRecorder
from bkuser.apps.tenant.models import TenantDepartment, TenantUser

logger = logging.getLogger(__name__)


class TenantSyncTaskContext:
    """同步任务上下文管理器"""

    batch_size = 250

    def __init__(self, task: TenantSyncTask):
        self.task = task
        self.logger = TaskLogger()
        self.recorder = ChangeLogRecorder()
        self.lock = TenantSyncTaskLock(task.tenant_id, task.data_source_id)

    def __enter__(self):
        logger.info(
            "start sync tenant, task_id: %s, data_source_id: %s, tenant_id: %s",
            self.task.id,
            self.task.data_source_id,
            self.task.tenant_id,
        )
        self.logger.info(f"tenant sync task started, task_id is {self.task.id}...")

        # 如果获取不到同步锁，应该直接退出
        if not self.lock.acquire():
            self.logger.error(
                f"failed to acquire tenant {self.task.tenant_id} data source {self.task.data_source_id} sync lock..."
            )
            self._update_task(SyncTaskStatus.FAILED)
            self._store_logs_into_db()
            raise TenantSyncInterrupted("failed to acquire tenant sync lock, exit...")

        # 继续执行同步逻辑
        self._update_task(SyncTaskStatus.RUNNING)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 成功或失败都需要释放锁（拿不到锁是不会进入 __exit__ 的）
        self.lock.release()

        if exc_type is None:
            self.logger.info("tenant sync task success!")
            self._update_task(SyncTaskStatus.SUCCESS)
            self._store_records_into_db()
            self._store_logs_into_db()
            return

        # 任务超时添加特殊提示
        if exc_type is SoftTimeLimitExceeded:
            self.logger.error(f"sync task timeout, max duration is {self.task.extras.get('sync_timeout')}s")

        self.logger.error(
            "tenant sync task failed! Data modifications in this sync step will be rollback.\n\n"
            f"Exception: {''.join(traceback.format_exception(exc_type, exc_val, exc_tb))}"
        )
        self._update_task(SyncTaskStatus.FAILED)
        self._store_logs_into_db()

    def _update_task(self, status: SyncTaskStatus):
        """更新 task 记录"""
        self.task.status = status.value
        update_fields = ["status", "updated_at"]

        # 到达稳定状态，再更新任务耗时等信息
        if status in [SyncTaskStatus.SUCCESS, SyncTaskStatus.FAILED]:
            self.task.duration = timezone.now() - self.task.start_at
            self.task.has_warning = self.logger.has_warning
            self.task.summary = {
                "user": {
                    "create": len(self.recorder.get(SyncOperation.CREATE, TenantSyncObjectType.USER)),
                    "delete": len(self.recorder.get(SyncOperation.DELETE, TenantSyncObjectType.USER)),
                },
                "department": {
                    "create": len(self.recorder.get(SyncOperation.CREATE, TenantSyncObjectType.DEPARTMENT)),
                    "delete": len(self.recorder.get(SyncOperation.DELETE, TenantSyncObjectType.DEPARTMENT)),
                },
            }
            update_fields += ["duration", "has_warning", "summary"]

        self.task.save(update_fields=update_fields)

    def _store_records_into_db(self):
        """将变更记录存入数据库"""
        # 用户变更记录
        if created_users := self.recorder.get(SyncOperation.CREATE, TenantSyncObjectType.USER):
            TenantUserChangeLog.objects.bulk_create(
                self._build_user_change_logs(SyncOperation.CREATE, created_users), batch_size=self.batch_size
            )

        if deleted_users := self.recorder.get(SyncOperation.DELETE, TenantSyncObjectType.USER):
            TenantUserChangeLog.objects.bulk_create(
                self._build_user_change_logs(SyncOperation.DELETE, deleted_users), batch_size=self.batch_size
            )

        # 部门变更记录
        if created_depts := self.recorder.get(SyncOperation.CREATE, TenantSyncObjectType.DEPARTMENT):
            TenantDepartmentChangeLog.objects.bulk_create(
                self._build_dept_change_logs(SyncOperation.CREATE, created_depts), batch_size=self.batch_size
            )

        if deleted_depts := self.recorder.get(SyncOperation.DELETE, TenantSyncObjectType.DEPARTMENT):
            TenantDepartmentChangeLog.objects.bulk_create(
                self._build_dept_change_logs(SyncOperation.DELETE, deleted_depts), batch_size=self.batch_size
            )

    def _build_user_change_logs(self, operation: SyncOperation, users: List[TenantUser]) -> List[TenantUserChangeLog]:
        if operation == SyncOperation.CREATE:
            # 由于 bulk_create 不会返回 id，因此当 operation 为 create 时候，需要通过查询获取真实的 ID
            users = TenantUser.objects.filter(
                data_source_user_id__in=[u.data_source_user_id for u in users], tenant=self.task.tenant
            )

        return [
            TenantUserChangeLog(
                task=self.task,
                tenant=self.task.tenant,
                data_source=self.task.data_source,
                operation=operation,
                tenant_user_id=u.id,
                data_source_user_id=u.data_source_user_id,
            )
            for u in users
        ]

    def _build_dept_change_logs(
        self, operation: SyncOperation, depts: List[TenantDepartment]
    ) -> List[TenantDepartmentChangeLog]:
        if operation == SyncOperation.CREATE:
            # 由于 bulk_create 不会返回 id，因此当 operation 为 create 时候，需要通过查询获取真实的 ID
            depts = TenantDepartment.objects.filter(
                data_source_department_id__in=[d.data_source_department_id for d in depts], tenant=self.task.tenant
            )

        return [
            TenantDepartmentChangeLog(
                task=self.task,
                tenant=self.task.tenant,
                data_source=self.task.data_source,
                operation=operation,
                tenant_department_id=d.id,
                data_source_department_id=d.data_source_department_id,
            )
            for d in depts
        ]

    def _store_logs_into_db(self):
        """将步骤日志存入数据库"""
        sync_task_logs = self.logger.logs.strip()
        self.task.logs = sync_task_logs
        self.task.save(update_fields=["logs", "updated_at"])
