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
import uuid
from datetime import timedelta

from django.db import models

from bkuser.apps.sync.constants import (
    DataSourceSyncObjectType,
    DataSourceSyncStepName,
    SyncOperation,
    SyncTaskStatus,
    SyncTaskTrigger,
    TenantSyncObjectType,
    TenantSyncStepName,
)
from bkuser.common.models import TimestampedModel


class DataSourceSyncTask(TimestampedModel):
    """数据源同步任务"""

    data_source_id = models.IntegerField("数据源 ID")
    status = models.CharField("任务总状态", choices=SyncTaskStatus.get_choices(), max_length=32)
    trigger = models.CharField("触发方式", choices=SyncTaskTrigger.get_choices(), max_length=32)
    operator = models.CharField("操作人", null=True, blank=True, default="", max_length=128)
    start_at = models.DateTimeField("任务开始时间", auto_now_add=True)
    duration = models.DurationField("任务持续时间", default=timedelta(seconds=0))
    extra = models.JSONField("扩展信息", default=dict)

    @property
    def summary(self):
        # TODO (su) 支持获取任务总结
        return "数据同步成功" if self.status == SyncTaskStatus.SUCCESS else "数据同步失败"


class DataSourceSyncStep(TimestampedModel):
    """数据源同步步骤"""

    task = models.ForeignKey(DataSourceSyncTask, on_delete=models.CASCADE, db_constraint=False, related_name="steps")
    object_type = models.CharField("对象类型", choices=DataSourceSyncObjectType.get_choices(), max_length=32)
    step_name = models.CharField("步骤名称", choices=DataSourceSyncStepName.get_choices(), max_length=32)
    status = models.CharField("当前步骤状态", choices=SyncTaskStatus.get_choices(), max_length=32)
    details = models.JSONField("详细信息", default=dict)
    logs = models.TextField("日志", default="")


class DataSourceUserChangeLog(TimestampedModel):
    """数据源用户变更日志"""

    id = models.UUIDField("变更日志 ID", default=uuid.uuid4, primary_key=True)
    task = models.ForeignKey(
        DataSourceSyncTask, on_delete=models.CASCADE, db_constraint=False, related_name="user_change_logs"
    )
    data_source_id = models.IntegerField("数据源 ID")
    user_id = models.CharField("数据源用户 ID", max_length=64)
    operation = models.CharField("操作类型", choices=SyncOperation.get_choices(), max_length=32)
    # 数据源原始数据
    user_code = models.CharField("用户唯一标识", max_length=128)
    username = models.CharField("用户名", max_length=128)
    full_name = models.CharField("用户全名", max_length=128)


class DataSourceDepartmentChangeLog(TimestampedModel):
    """数据源部门变更日志"""

    id = models.UUIDField("变更日志 ID", default=uuid.uuid4, primary_key=True)
    task = models.ForeignKey(
        DataSourceSyncTask, on_delete=models.CASCADE, db_constraint=False, related_name="department_change_logs"
    )
    data_source_id = models.IntegerField("数据源 ID")
    operation = models.CharField("操作类型", choices=SyncOperation.get_choices(), max_length=32)
    department_id = models.CharField("数据源部门 ID", max_length=128)
    # 数据源原始数据
    department_code = models.CharField("部门唯一标识", max_length=128)
    department_name = models.CharField("部门名称", max_length=255)


class TenantSyncTask(TimestampedModel):
    """租户同步任务"""

    tenant_id = models.IntegerField("租户 ID")
    data_source_id = models.IntegerField("数据源 ID")
    status = models.CharField("任务总状态", choices=SyncTaskStatus.get_choices(), max_length=32)
    trigger = models.CharField("触发方式", choices=SyncTaskTrigger.get_choices(), max_length=32)
    operator = models.CharField("操作人", null=True, blank=True, default="", max_length=128)
    start_at = models.DateTimeField("任务开始时间", auto_now_add=True)
    duration = models.DurationField("任务持续时间", default=timedelta(seconds=0))
    extra = models.JSONField("扩展信息", default=dict)

    @property
    def summary(self):
        # TODO (su) 支持获取任务总结
        return "数据同步成功" if self.status == SyncTaskStatus.SUCCESS else "数据同步失败"


class TenantSyncStep(TimestampedModel):
    """租户同步任务步骤"""

    task = models.ForeignKey(TenantSyncTask, on_delete=models.CASCADE, db_constraint=False, related_name="steps")
    object_type = models.CharField("对象类型", choices=TenantSyncObjectType.get_choices(), max_length=32)
    step_name = models.CharField("步骤名称", choices=TenantSyncStepName.get_choices(), max_length=32)
    status = models.CharField("当前步骤状态", choices=SyncTaskStatus.get_choices(), max_length=32)
    details = models.JSONField("详细信息", default=dict)
    logs = models.TextField("日志", default="")


class TenantUserChangeLog(TimestampedModel):
    """租户用户变更日志"""

    id = models.UUIDField("变更日志 ID", default=uuid.uuid4, primary_key=True)
    task = models.ForeignKey(
        TenantSyncTask, on_delete=models.CASCADE, db_constraint=False, related_name="user_change_logs"
    )
    tenant_id = models.IntegerField("租户 ID")
    data_source_id = models.IntegerField("数据源 ID")
    operation = models.CharField("操作类型", choices=SyncOperation.get_choices(), max_length=32)
    user_id = models.CharField("用户 ID", max_length=64)
    username = models.CharField("用户名", max_length=128)
    full_name = models.CharField("用户全名", max_length=128)


class TenantDepartmentChangeLog(TimestampedModel):
    """租户部门变更日志"""

    id = models.UUIDField("变更日志 ID", default=uuid.uuid4, primary_key=True)
    task = models.ForeignKey(
        TenantSyncTask, on_delete=models.CASCADE, db_constraint=False, related_name="department_change_logs"
    )
    tenant_id = models.IntegerField("租户 ID")
    data_source_id = models.IntegerField("数据源 ID")
    operation = models.CharField("操作类型", choices=SyncOperation.get_choices(), max_length=32)
    department_id = models.CharField("部门 ID", max_length=128)
    department_name = models.CharField("部门名称", max_length=255)
