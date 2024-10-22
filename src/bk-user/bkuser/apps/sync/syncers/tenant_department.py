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

# ignore custom logger must use %s string format in this file
# ruff: noqa: G004
from django.db import transaction

from bkuser.apps.data_source.models import DataSource, DataSourceDepartment
from bkuser.apps.sync.constants import SyncOperation, TenantSyncObjectType
from bkuser.apps.sync.contexts import TenantSyncTaskContext
from bkuser.apps.tenant.models import Tenant, TenantDepartment, TenantDepartmentIDRecord
from bkuser.apps.tenant.utils import TenantDeptIDGenerator


class TenantDepartmentSyncer:
    """租户部门同步器"""

    batch_size = 250

    def __init__(self, ctx: TenantSyncTaskContext, data_source: DataSource, tenant: Tenant):
        self.ctx = ctx
        self.data_source = data_source
        self.tenant = tenant

    def sync(self):
        """TODO (su) 协同支持指定数据范围后，需要考虑限制"""
        exists_tenant_departments = TenantDepartment.objects.filter(tenant=self.tenant, data_source=self.data_source)
        data_source_departments = DataSourceDepartment.objects.filter(data_source=self.data_source)

        # 删除掉租户中存在的，但是数据源中不存在的
        waiting_delete_tenant_departments = exists_tenant_departments.exclude(
            data_source_department__in=data_source_departments
        )

        # 数据源中存在，但是租户中不存在的，需要创建
        waiting_sync_data_source_departments = data_source_departments.exclude(
            id__in=[u.data_source_department_id for u in exists_tenant_departments]
        )
        waiting_create_tenant_departments = [
            TenantDepartment(
                id=TenantDeptIDGenerator(self.tenant.id, self.data_source).gen(dept),
                tenant=self.tenant,
                data_source_department=dept,
                data_source=self.data_source,
            )
            for dept in waiting_sync_data_source_departments
        ]

        # 统一在事务中对租户部门进行变更，先删除再增加
        with transaction.atomic():
            waiting_delete_tenant_departments.delete()
            TenantDepartment.objects.bulk_create(waiting_create_tenant_departments, batch_size=self.batch_size)

            # 批量记录租户部门 ID（后续有复用需求）
            records = [
                TenantDepartmentIDRecord(
                    tenant=self.tenant,
                    data_source=self.data_source,
                    code=dept.data_source_department.code,
                    tenant_department_id=dept.id,
                )
                for dept in TenantDepartment.objects.filter(
                    tenant=self.tenant, data_source_department__in=waiting_sync_data_source_departments
                ).select_related("data_source_department")
            ]
            # 由于存量历史数据（Record）也会被下发，因此需要忽略冲突保证其他数据可以正常插入
            TenantDepartmentIDRecord.objects.bulk_create(records, batch_size=self.batch_size, ignore_conflicts=True)

        # 记录删除日志，变更记录
        self.ctx.logger.info(f"delete {len(waiting_delete_tenant_departments)} tenant departments")
        self.ctx.recorder.add(SyncOperation.DELETE, TenantSyncObjectType.DEPARTMENT, waiting_delete_tenant_departments)

        # 记录创建日志，变更记录
        self.ctx.logger.info(f"create {len(waiting_create_tenant_departments)} tenant departments")
        self.ctx.recorder.add(SyncOperation.CREATE, TenantSyncObjectType.DEPARTMENT, waiting_create_tenant_departments)
