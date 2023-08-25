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

from django.db import models

from bkuser.apps.sync.constants import (
    DataSourceSyncStepName,
    SyncOperate,
    SyncTaskStatus,
    SyncTaskTrigger,
    TenantSyncStepName,
)
from bkuser.common.models import TimestampedModel


class DataSourceSyncTask(TimestampedModel):
    """数据源同步任务"""

    data_source_id = models.IntegerField("数据源 ID")
    status = models.CharField("任务总状态", choices=SyncTaskStatus.get_django_choices(), max_length=32)
    trigger = models.CharField("触发方式", choices=SyncTaskTrigger.get_django_choices(), max_length=32)
    start_time = models.DateTimeField("任务开始时间")
    duration = models.DurationField("任务持续时间")


class DataSourceSyncStep(TimestampedModel):
    """数据源同步步骤"""

    task_id = models.BigIntegerField("任务 ID")
    step_name = models.CharField("步骤名称", choices=DataSourceSyncStepName.get_django_choices(), max_length=32)
    status = models.CharField("当前步骤状态", choices=SyncTaskStatus.get_django_choices(), max_length=32)
    details = models.JSONField("详细信息", default=dict)
    logs = models.TextField("日志", default="")


class DataSourceUserChangeLog(TimestampedModel):
    """数据源用户变更日志"""

    id = models.UUIDField("变更日志 ID", default=uuid.uuid4, primary_key=True)
    task_id = models.BigIntegerField("任务 ID")
    data_source_id = models.IntegerField("数据源 ID")
    user_id = models.CharField("数据源用户 ID", max_length=64)
    operate = models.CharField("操作类型", choices=SyncOperate.get_django_choices(), max_length=32)
    # 数据源原始数据
    user_code = models.CharField("用户唯一标识", max_length=128)
    username = models.CharField("用户名", max_length=128)
    full_name = models.CharField("用户全名", max_length=128)
    department_id = models.CharField("部门 ID", max_length=128)


class DataSourceDepartmentChangeLog(TimestampedModel):
    """数据源部门变更日志"""

    id = models.UUIDField("变更日志 ID", default=uuid.uuid4, primary_key=True)
    task_id = models.BigIntegerField("任务 ID")
    data_source_id = models.IntegerField("数据源 ID")
    operate = models.CharField("操作类型", choices=SyncOperate.get_django_choices(), max_length=32)
    department_id = models.CharField("数据源部门 ID", max_length=128)
    # 数据源原始数据
    department_code = models.CharField("部门唯一标识", max_length=128)
    department_name = models.CharField("部门名称", max_length=255)


class TenantSyncTask(TimestampedModel):
    """租户同步任务"""

    tenant_id = models.IntegerField("租户 ID")
    data_source_id = models.IntegerField("数据源 ID")
    status = models.CharField("任务总状态", max_length=32)
    trigger = models.CharField("触发方式", choices=SyncTaskTrigger.get_django_choices(), max_length=32)
    start_time = models.DateTimeField("任务开始时间")
    duration = models.DurationField("任务持续时间")


class TenantSyncStep(TimestampedModel):
    """租户同步任务步骤"""

    task_id = models.BigIntegerField("任务 ID")
    step_name = models.CharField("步骤名称", choices=TenantSyncStepName.get_django_choices(), max_length=32)
    status = models.CharField("当前步骤状态", choices=SyncTaskStatus.get_django_choices(), max_length=32)
    details = models.JSONField("详细信息", default=dict)
    logs = models.TextField("日志", default="")


class TenantUserChangeLog(TimestampedModel):
    """租户用户变更日志"""

    id = models.UUIDField("变更日志 ID", default=uuid.uuid4, primary_key=True)
    task_id = models.BigIntegerField("任务 ID")
    tenant_id = models.IntegerField("租户 ID")
    data_source_id = models.IntegerField("数据源 ID")
    operate = models.CharField("操作类型", choices=SyncOperate.get_django_choices(), max_length=32)
    user_id = models.CharField("用户 ID", max_length=64)
    username = models.CharField("用户名", max_length=128)
    full_name = models.CharField("用户全名", max_length=128)
    department_id = models.CharField("部门 ID", max_length=128)


class TenantDepartmentChangeLog(TimestampedModel):
    """租户部门变更日志"""

    id = models.UUIDField("变更日志 ID", default=uuid.uuid4, primary_key=True)
    task_id = models.BigIntegerField("任务 ID")
    tenant_id = models.IntegerField("租户 ID")
    data_source_id = models.IntegerField("数据源 ID")
    operate = models.CharField("操作类型", choices=SyncOperate.get_django_choices(), max_length=32)
    department_id = models.CharField("部门 ID", max_length=128)
    department_name = models.CharField("部门名称", max_length=255)
