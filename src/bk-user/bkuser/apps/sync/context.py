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
import io
import logging
import traceback
from collections import defaultdict
from functools import partialmethod
from typing import Callable, Dict, List, Tuple

from django.utils import timezone

from bkuser.apps.data_source.models import DataSourceDepartment, DataSourceUser
from bkuser.apps.sync.constants import (
    DataSourceSyncObjectType,
    SyncLogLevel,
    SyncOperation,
    SyncTaskStatus,
    TenantSyncObjectType,
)
from bkuser.apps.sync.models import (
    DataSourceDepartmentChangeLog,
    DataSourceSyncTask,
    DataSourceUserChangeLog,
    TenantDepartmentChangeLog,
    TenantSyncTask,
    TenantUserChangeLog,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantUser

logger = logging.getLogger(__name__)

# 二元组对象，用于以何种方式，操作某类对象
SyncOperationObjectType = Tuple[SyncOperation, DataSourceSyncObjectType | TenantSyncObjectType]


class TaskLogger:
    """任务日志记录器"""

    has_warning: bool
    _buffer: io.StringIO

    def __init__(self):
        self.has_warning = False
        self._buffer = io.StringIO()

    @property
    def logs(self):
        return self._buffer.getvalue()

    def _log(self, level: SyncLogLevel, msg: str):
        if level == SyncLogLevel.WARNING:
            self.has_warning = True

        self._buffer.write(f"{level.value} {msg}\n\n")

    # TODO (su) 支持 debug 级别的日志？但只能通过 shell 组装的 task 才能触发？
    info: Callable = partialmethod(_log, SyncLogLevel.INFO)  # type: ignore
    warning: Callable = partialmethod(_log, SyncLogLevel.WARNING)  # type: ignore
    error: Callable = partialmethod(_log, SyncLogLevel.ERROR)  # type: ignore


class ChangeLogRecorder:
    """变更日志记录器"""

    records: Dict[SyncOperationObjectType, List]

    def __init__(self):
        self.records = defaultdict(list)

    def add(
        self,
        operation: SyncOperation,
        type: DataSourceSyncObjectType | TenantSyncObjectType,
        items: List[DataSourceUser | DataSourceDepartment | TenantUser | TenantDepartment],
    ):
        """添加某类型某操作的变更日志"""
        self.records[(operation, type)].extend(items)

    def get(
        self, operation: SyncOperation, type: DataSourceSyncObjectType | TenantSyncObjectType
    ) -> List[DataSourceUser | DataSourceDepartment | TenantUser | TenantDepartment]:
        """获取某类型某操作的变更日志"""
        return self.records[(operation, type)]


class DataSourceSyncTaskContext:
    """同步任务上下文管理器"""

    batch_size = 250

    def __init__(self, task: DataSourceSyncTask):
        self.task = task
        self.logger = TaskLogger()
        self.recorder = ChangeLogRecorder()

    def __enter__(self):
        logger.info(
            "start sync data source, task_id: %s, data_source_id: %s",
            self.task.id,
            self.task.data_source_id,
        )
        self.logger.info(f"sync task started, task_id is {self.task.id}...")  # noqa: G004
        self._update_task_status(SyncTaskStatus.RUNNING)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.logger.info("sync task success!")
            self._update_task_status(SyncTaskStatus.SUCCESS)
            self._store_records_into_db()
            self._store_logs_into_db()
            return

        # 同步过程中出现异常，需要记录日志，并抛出 DataSourceSyncError
        self.logger.error(
            "sync task failed! All data modifications in this sync will be rollback.\n\n"  # noqa: G004
            f"Exception: {''.join(traceback.format_exception(exc_type, exc_val, exc_tb))}"
        )
        self._update_task_status(SyncTaskStatus.FAILED)
        self._store_logs_into_db()

    def _update_task_status(self, status: SyncTaskStatus):
        """任务完成/失败后更新 task 状态"""
        self.task.status = status.value
        self.task.duration = timezone.now() - self.task.start_at
        self.task.has_warning = self.logger.has_warning
        self.task.save(update_fields=["status", "duration", "has_warning", "updated_at"])

    def _store_records_into_db(self):
        """将变更记录存入数据库"""
        # 用户变更记录
        if created_users := self.recorder.get(SyncOperation.CREATE, DataSourceSyncObjectType.USER):
            DataSourceUserChangeLog.objects.bulk_create(
                self._build_user_change_logs(SyncOperation.CREATE, created_users), batch_size=self.batch_size
            )

        if deleted_users := self.recorder.get(SyncOperation.DELETE, DataSourceSyncObjectType.USER):
            DataSourceUserChangeLog.objects.bulk_create(
                self._build_user_change_logs(SyncOperation.DELETE, deleted_users), batch_size=self.batch_size
            )

        if updated_users := self.recorder.get(SyncOperation.UPDATE, DataSourceSyncObjectType.USER):
            DataSourceUserChangeLog.objects.bulk_create(
                self._build_user_change_logs(SyncOperation.UPDATE, updated_users), batch_size=self.batch_size
            )

        # 部门变更记录
        if created_depts := self.recorder.get(SyncOperation.CREATE, DataSourceSyncObjectType.DEPARTMENT):
            DataSourceDepartmentChangeLog.objects.bulk_create(
                self._build_dept_change_logs(SyncOperation.CREATE, created_depts), batch_size=self.batch_size
            )

        if deleted_depts := self.recorder.get(SyncOperation.DELETE, DataSourceSyncObjectType.DEPARTMENT):
            DataSourceDepartmentChangeLog.objects.bulk_create(
                self._build_dept_change_logs(SyncOperation.DELETE, deleted_depts), batch_size=self.batch_size
            )

        if updated_depts := self.recorder.get(SyncOperation.UPDATE, DataSourceSyncObjectType.DEPARTMENT):
            DataSourceDepartmentChangeLog.objects.bulk_create(
                self._build_dept_change_logs(SyncOperation.UPDATE, updated_depts), batch_size=self.batch_size
            )

    def _build_user_change_logs(
        self, operation: SyncOperation, users: List[DataSourceUser]
    ) -> List[DataSourceUserChangeLog]:
        if operation == SyncOperation.CREATE:
            # 由于 bulk_create 不会返回 id，因此当 operation 为 create 时候，需要通过查询获取真实的 ID
            users = DataSourceUser.objects.filter(code__in=[u.code for u in users], data_source=self.task.data_source)

        return [
            DataSourceUserChangeLog(
                task=self.task,
                data_source=self.task.data_source,
                operation=operation,
                user_id=u.id,
                user_code=u.code,
                username=u.username,
                full_name=u.full_name,
            )
            for u in users
        ]

    def _build_dept_change_logs(
        self, operation: SyncOperation, depts: List[DataSourceDepartment]
    ) -> List[DataSourceDepartmentChangeLog]:
        if operation == SyncOperation.CREATE:
            # 由于 bulk_create 不会返回 id，因此当 operation 为 create 时候，需要通过查询获取真实的 ID
            depts = DataSourceDepartment.objects.filter(
                code__in=[d.code for d in depts], data_source=self.task.data_source
            )

        return [
            DataSourceDepartmentChangeLog(
                task=self.task,
                data_source=self.task.data_source,
                operation=operation,
                department_id=d.id,
                department_code=d.code,
                department_name=d.name,
            )
            for d in depts
        ]

    def _store_logs_into_db(self):
        """将步骤日志存入数据库"""
        sync_task_logs = self.logger.logs
        logger.info("data source sync task %s logs:\n%s", self.task.id, sync_task_logs)
        self.task.logs = sync_task_logs
        self.task.save(update_fields=["logs", "updated_at"])


class TenantSyncTaskContext:
    """同步任务上下文管理器"""

    batch_size = 250

    def __init__(self, task: TenantSyncTask):
        self.task = task
        self.logger = TaskLogger()
        self.recorder = ChangeLogRecorder()

    def __enter__(self):
        logger.info(
            "start sync tenant, task_id: %s, data_source_id: %s, tenant_id: %s",
            self.task.id,
            self.task.data_source_id,
            self.task.tenant_id,
        )
        self.logger.info(f"sync task started, task_id is {self.task.id}...")  # noqa: G004
        self._update_task_status(SyncTaskStatus.RUNNING)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.logger.info("sync task success!")
            self._update_task_status(SyncTaskStatus.SUCCESS)
            self._store_records_into_db()
            self._store_logs_into_db()
            return

        # 同步过程中出现异常，需要记录日志，并抛出 TenantSyncError
        self.logger.error(
            "sync task failed! All data modifications in this sync will be rollback.\n\n"  # noqa: G004
            f"Exception: {''.join(traceback.format_exception(exc_type, exc_val, exc_tb))}"
        )
        self._update_task_status(SyncTaskStatus.FAILED)
        self._store_logs_into_db()

    def _update_task_status(self, status: SyncTaskStatus):
        """任务完成/失败后更新 task 状态"""
        self.task.status = status.value
        self.task.duration = timezone.now() - self.task.start_at
        self.task.has_warning = self.logger.has_warning
        self.task.save(update_fields=["status", "duration", "has_warning", "updated_at"])

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

        if updated_users := self.recorder.get(SyncOperation.UPDATE, TenantSyncObjectType.USER):
            TenantUserChangeLog.objects.bulk_create(
                self._build_user_change_logs(SyncOperation.UPDATE, updated_users), batch_size=self.batch_size
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

        if updated_depts := self.recorder.get(SyncOperation.UPDATE, TenantSyncObjectType.DEPARTMENT):
            TenantDepartmentChangeLog.objects.bulk_create(
                self._build_dept_change_logs(SyncOperation.UPDATE, updated_depts), batch_size=self.batch_size
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
                user_id=u.id,
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
                department_id=d.id,
            )
            for d in depts
        ]

    def _store_logs_into_db(self):
        """将步骤日志存入数据库"""
        sync_task_logs = self.logger.logs
        logger.info("tenant task %s logs:\n%s", self.task.id, sync_task_logs)
        self.task.logs = sync_task_logs
        self.task.save(update_fields=["logs", "updated_at"])
