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

from typing import Set

import pytest
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
)
from bkuser.apps.sync.syncers import TenantDepartmentSyncer
from bkuser.apps.tenant.models import Tenant, TenantDepartment

pytestmark = pytest.mark.django_db


class TestTenantDepartmentSyncer:
    def test_standard(self, tenant_sync_task_ctx, full_local_data_source, random_tenant):
        # 初始化场景
        TenantDepartmentSyncer(tenant_sync_task_ctx, full_local_data_source, random_tenant).sync()
        assert self._gen_ds_dept_ids_with_data_source(
            data_source=full_local_data_source
        ) == self._gen_ds_dept_ids_with_tenant(random_tenant, full_local_data_source)

        # 更新场景
        DataSourceDepartment.objects.filter(
            data_source=full_local_data_source, code__in=["center_ba", "group_baa"]
        ).delete()
        DataSourceDepartment.objects.create(data_source=full_local_data_source, code="center_ac", name="中心AC")

        TenantDepartmentSyncer(tenant_sync_task_ctx, full_local_data_source, random_tenant).sync()
        assert self._gen_ds_dept_ids_with_data_source(
            data_source=full_local_data_source
        ) == self._gen_ds_dept_ids_with_tenant(random_tenant, full_local_data_source)

        # 删除场景，只会删除当前数据源关联的租户部门
        DataSourceDepartment.objects.filter(data_source=full_local_data_source).delete()
        TenantDepartmentSyncer(tenant_sync_task_ctx, full_local_data_source, random_tenant).sync()

        assert not TenantDepartment.objects.filter(tenant=random_tenant, data_source=full_local_data_source).exists()

    @staticmethod
    def _gen_ds_dept_ids_with_tenant(tenant: Tenant, data_source: DataSource) -> Set[int]:
        return set(
            TenantDepartment.objects.filter(
                tenant=tenant,
                data_source=data_source,
            ).values_list("data_source_department_id", flat=True)
        )

    @staticmethod
    def _gen_ds_dept_ids_with_data_source(data_source: DataSource) -> Set[int]:
        return set(
            DataSourceDepartment.objects.filter(
                data_source=data_source,
            ).values_list("id", flat=True)
        )
