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
from datetime import timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _

from bkuser.apps.data_source.models import DataSource
from bkuser.apps.sync.constants import SyncOperation, SyncTaskStatus, SyncTaskTrigger
from bkuser.apps.tenant.models import Tenant
from bkuser.common.models import TimestampedModel
from bkuser.common.time import datetime_to_display
from bkuser.utils.uuid import generate_uuid


class DataSourceSyncTask(TimestampedModel):
    """数据源同步任务"""

    data_source = models.ForeignKey(DataSource, on_delete=models.DO_NOTHING, db_constraint=False)
    status = models.CharField("任务总状态", choices=SyncTaskStatus.get_choices(), max_length=32)
    has_warning = models.BooleanField("任务执行是否有警告", default=False)
    trigger = models.CharField("触发方式", choices=SyncTaskTrigger.get_choices(), max_length=32)
    operator = models.CharField("操作人", null=True, blank=True, default="", max_length=128)
    start_at = models.DateTimeField("任务开始时间", auto_now_add=True)
    duration = models.DurationField("任务持续时间", default=timedelta(seconds=0))
    logs = models.TextField("任务日志", default="")
    extras = models.JSONField("扩展信息", default=dict)

    class Meta:
        ordering = ["-id"]

    @property
    def summary(self):
        # 异步模式
        if self.extras.get("async_run", False):
            if self.status in [SyncTaskStatus.PENDING, SyncTaskStatus.RUNNING]:
                return _("数据源同步任务执行中")
            if self.status == SyncTaskStatus.SUCCESS:
                return _("数据源同步成功")

            return _("数据源同步失败，请前往 `数据更新记录` 查看日志详情")

        # 同步模式
        return _("数据源导入成功") if self.status == SyncTaskStatus.SUCCESS else _("数据源导入失败")

    @property
    def start_at_display(self) -> str:
        return datetime_to_display(self.start_at)


class DataSourceUserChangeLog(TimestampedModel):
    """数据源用户变更日志"""

    id = models.UUIDField("变更日志 ID", default=generate_uuid, primary_key=True)
    task = models.ForeignKey(
        DataSourceSyncTask, on_delete=models.CASCADE, db_constraint=False, related_name="user_change_logs"
    )
    data_source = models.ForeignKey(DataSource, on_delete=models.DO_NOTHING, db_constraint=False)
    user_id = models.CharField("数据源用户 ID", max_length=64)
    operation = models.CharField("操作类型", choices=SyncOperation.get_choices(), max_length=32)
    # 数据源原始数据
    user_code = models.CharField("用户唯一标识", max_length=128)
    username = models.CharField("用户名", max_length=128)
    full_name = models.CharField("用户姓名", max_length=128)


class DataSourceDepartmentChangeLog(TimestampedModel):
    """数据源部门变更日志"""

    id = models.UUIDField("变更日志 ID", default=generate_uuid, primary_key=True)
    task = models.ForeignKey(
        DataSourceSyncTask, on_delete=models.CASCADE, db_constraint=False, related_name="department_change_logs"
    )
    data_source = models.ForeignKey(DataSource, on_delete=models.DO_NOTHING, db_constraint=False)
    operation = models.CharField("操作类型", choices=SyncOperation.get_choices(), max_length=32)
    department_id = models.CharField("数据源部门 ID", max_length=128)
    # 数据源原始数据
    department_code = models.CharField("部门唯一标识", max_length=128)
    department_name = models.CharField("部门名称", max_length=255)


class TenantSyncTask(TimestampedModel):
    """租户同步任务"""

    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, db_constraint=False)
    data_source = models.ForeignKey(DataSource, on_delete=models.DO_NOTHING, db_constraint=False)
    status = models.CharField("任务总状态", choices=SyncTaskStatus.get_choices(), max_length=32)
    has_warning = models.BooleanField("任务执行是否有警告", default=False)
    trigger = models.CharField("触发方式", choices=SyncTaskTrigger.get_choices(), max_length=32)
    operator = models.CharField("操作人", null=True, blank=True, default="", max_length=128)
    start_at = models.DateTimeField("任务开始时间", auto_now_add=True)
    duration = models.DurationField("任务持续时间", default=timedelta(seconds=0))
    logs = models.TextField("任务日志", default="")
    extras = models.JSONField("扩展信息", default=dict)

    class Meta:
        ordering = ["-id"]

    @property
    def summary(self):
        # 异步模式
        if self.extras.get("async_run", False):
            if self.status in [SyncTaskStatus.PENDING, SyncTaskStatus.RUNNING]:
                return _("租户数据同步任务执行中")
            if self.status == SyncTaskStatus.SUCCESS:
                return _("租户数据同步成功")

            return _("租户数据同步失败")

        # 租户数据同步不应该有同步模式，都是异步行为
        return f"Why tenant sync task {self.id} can run in sync mode? Please report this to the administrator."

    @property
    def start_at_display(self) -> str:
        return datetime_to_display(self.start_at)


class TenantUserChangeLog(TimestampedModel):
    """租户用户变更日志"""

    id = models.UUIDField("变更日志 ID", default=generate_uuid, primary_key=True)
    task = models.ForeignKey(
        TenantSyncTask, on_delete=models.CASCADE, db_constraint=False, related_name="user_change_logs"
    )
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, db_constraint=False)
    data_source = models.ForeignKey(DataSource, on_delete=models.DO_NOTHING, db_constraint=False)
    operation = models.CharField("操作类型", choices=SyncOperation.get_choices(), max_length=32)
    user_id = models.CharField("用户 ID", max_length=64)


class TenantDepartmentChangeLog(TimestampedModel):
    """租户部门变更日志"""

    id = models.UUIDField("变更日志 ID", default=generate_uuid, primary_key=True)
    task = models.ForeignKey(
        TenantSyncTask, on_delete=models.CASCADE, db_constraint=False, related_name="department_change_logs"
    )
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, db_constraint=False)
    data_source = models.ForeignKey(DataSource, on_delete=models.DO_NOTHING, db_constraint=False)
    operation = models.CharField("操作类型", choices=SyncOperation.get_choices(), max_length=32)
    department_id = models.CharField("部门 ID", max_length=128)
