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
import pytest
from bkuser.apps.data_source.models import DataSourceDepartment, DataSourceUser
from bkuser.apps.sync.constants import DataSourceSyncObjectType, SyncOperation, SyncTaskStatus
from bkuser.apps.sync.context import ChangeLogRecorder, DataSourceSyncTaskContext, TaskLogger, TenantSyncTaskContext
from bkuser.apps.sync.models import (
    DataSourceDepartmentChangeLog,
    DataSourceUserChangeLog,
    TenantDepartmentChangeLog,
    TenantUserChangeLog,
)
from bkuser.apps.sync.syncers import TenantDepartmentSyncer, TenantUserSyncer

pytestmark = pytest.mark.django_db


class TestTaskLogger:
    def test_logs(self):
        logger = TaskLogger()
        logger.info("start test logger")
        logger.info("this is info log")
        logger.warning("this is warning log")
        logger.error("this is error log")

        assert logger.logs == (
            "INFO start test logger\n\n"
            "INFO this is info log\n\n"
            "WARNING this is warning log\n\n"
            "ERROR this is error log\n\n"
        )

    def test_has_warning(self):
        logger = TaskLogger()
        logger.info("this is info log")
        assert not logger.has_warning

        logger.warning("this is warning log")
        assert logger.has_warning


class TestChangeLogRecorder:
    def test_normal(self, full_general_data_source):
        users = list(DataSourceUser.objects.filter(data_source=full_general_data_source))
        departments = list(DataSourceDepartment.objects.filter(data_source=full_general_data_source))

        recorder = ChangeLogRecorder()
        recorder.add(operation=SyncOperation.CREATE, type=DataSourceSyncObjectType.USER, items=users)
        recorder.add(operation=SyncOperation.CREATE, type=DataSourceSyncObjectType.USER, items=users)

        recorder.add(operation=SyncOperation.CREATE, type=DataSourceSyncObjectType.DEPARTMENT, items=departments)

        assert len(recorder.get(operation=SyncOperation.CREATE, type=DataSourceSyncObjectType.USER)) == len(users) * 2
        assert recorder.get(operation=SyncOperation.CREATE, type=DataSourceSyncObjectType.DEPARTMENT) == departments


class TestDataSourceSyncTaskContext:
    def test_failed_task(self, data_source_sync_task):
        with pytest.raises(ValueError, match="error"), DataSourceSyncTaskContext(data_source_sync_task):
            raise ValueError("data source task config error!")

        assert data_source_sync_task.status == SyncTaskStatus.FAILED

        logs = data_source_sync_task.logs
        assert "INFO sync task started" in logs
        assert "ERROR sync task failed! All data modifications in this sync will be rollback." in logs

    def test_success_task_without_warning(self, data_source_sync_task):
        with DataSourceSyncTaskContext(data_source_sync_task) as ctx:
            ctx.logger.info("this is info log")

        assert data_source_sync_task.status == SyncTaskStatus.SUCCESS
        assert not data_source_sync_task.has_warning

        logs = data_source_sync_task.logs
        assert "INFO sync task started" in logs
        assert "INFO this is info log" in logs
        assert "INFO sync task success!" in logs

    def test_success_task_has_warning(self, data_source_sync_task):
        with DataSourceSyncTaskContext(data_source_sync_task) as ctx:
            ctx.logger.info("this is info log")
            ctx.logger.warning("this is warning log")

        assert data_source_sync_task.status == SyncTaskStatus.SUCCESS
        assert data_source_sync_task.has_warning
        assert "this is warning log" in data_source_sync_task.logs

    def test_with_records(self, data_source_sync_task):
        ds = data_source_sync_task.data_source
        zhangsan = DataSourceUser(
            code="zhangsan",
            username="zhangsan",
            full_name="张三",
            email="zhangsan@m.com",
            phone="13512345671",
            data_source=ds,
        )
        lisi = DataSourceUser(
            id=2,
            code="lisi",
            username="lisi",
            full_name="李四",
            email="lisi@m.com",
            phone="13512345672",
            data_source=ds,
        )
        zhangsan.save()

        depts = [
            DataSourceDepartment(id=1, data_source=ds, code="company", name="公司"),
            DataSourceDepartment(id=2, data_source=ds, code="dept_a", name="部门A"),
            DataSourceDepartment(id=3, data_source=ds, code="dept_b", name="部门B"),
        ]
        with DataSourceSyncTaskContext(data_source_sync_task) as ctx:
            ctx.recorder.add(
                operation=SyncOperation.CREATE, type=DataSourceSyncObjectType.USER, items=[zhangsan, lisi]
            )
            ctx.recorder.add(operation=SyncOperation.UPDATE, type=DataSourceSyncObjectType.USER, items=[lisi])
            ctx.recorder.add(operation=SyncOperation.DELETE, type=DataSourceSyncObjectType.DEPARTMENT, items=depts)

        user_change_logs = DataSourceUserChangeLog.objects.filter(task=data_source_sync_task)
        # 创建类数据，会再查询一次 DB，因此 DB 中没有数据的（lisi），不会记录
        assert set(
            user_change_logs.filter(operation=SyncOperation.CREATE).values_list("user_code", flat=True),
        ) == {"zhangsan"}
        # 更新 / 删除类的数据，给啥就记录啥
        assert set(
            user_change_logs.filter(operation=SyncOperation.UPDATE).values_list("user_code", flat=True),
        ) == {"lisi"}
        assert DataSourceDepartmentChangeLog.objects.filter(task=data_source_sync_task).count() == len(depts)


class TestTenantSyncTaskContext:
    def test_failed_task(self, tenant_sync_task):
        with pytest.raises(ValueError, match="error"), TenantSyncTaskContext(tenant_sync_task):
            raise ValueError("tenant task config error!")

        assert tenant_sync_task.status == SyncTaskStatus.FAILED

        logs = tenant_sync_task.logs
        assert "tenant task config error!" in logs
        assert "ERROR sync task failed! All data modifications in this sync will be rollback." in logs

    def test_success_task_without_warning(self, tenant_sync_task):
        with TenantSyncTaskContext(tenant_sync_task) as ctx:
            ctx.logger.info("this is info log")

        assert tenant_sync_task.status == SyncTaskStatus.SUCCESS
        assert not tenant_sync_task.has_warning

        logs = tenant_sync_task.logs
        assert "INFO sync task started" in logs
        assert "INFO this is info log" in logs
        assert "INFO sync task success!" in logs

    def test_success_task_has_warning(self, tenant_sync_task):
        with TenantSyncTaskContext(tenant_sync_task) as ctx:
            ctx.logger.warning("this is warning log")

        assert tenant_sync_task.status == SyncTaskStatus.SUCCESS
        assert tenant_sync_task.has_warning
        assert "this is warning log" in tenant_sync_task.logs

    def test_with_records(self, default_tenant, tenant_sync_task, full_local_data_source):
        with TenantSyncTaskContext(tenant_sync_task) as ctx:
            TenantDepartmentSyncer(ctx, full_local_data_source, default_tenant).sync()
            TenantUserSyncer(ctx, full_local_data_source, default_tenant).sync()

        assert tenant_sync_task.logs != ""
        assert tenant_sync_task.status == SyncTaskStatus.SUCCESS
        assert TenantDepartmentChangeLog.objects.filter(task=tenant_sync_task).count() == 9  # noqa: PLR2004
        assert TenantUserChangeLog.objects.filter(task=tenant_sync_task).count() == 11  # noqa: PLR2004
