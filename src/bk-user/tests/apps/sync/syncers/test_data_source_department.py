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

from typing import List, Set, Tuple

import pytest
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentRelation,
)
from bkuser.apps.sync.context import DataSourceSyncTaskContext
from bkuser.apps.sync.syncers import DataSourceDepartmentSyncer
from bkuser.apps.sync.syncers.data_source_department import DataSourceDepartmentRelationSyncer
from bkuser.plugins.models import RawDataSourceDepartment

pytestmark = pytest.mark.django_db


class TestSyncDataSourceDepartment:
    """数据源部门同步流程测试"""

    def test_initial(self, data_source_sync_task_ctx, bare_local_data_source, raw_departments):
        self._sync_data_source_departments(
            data_source_sync_task_ctx, bare_local_data_source, raw_departments, overwrite=True, incremental=False
        )

        # 验证部门信息
        departments = DataSourceDepartment.objects.filter(data_source=bare_local_data_source)
        assert departments.count() == len(raw_departments)
        assert set(departments.values_list("code", flat=True)) == {dept.code for dept in raw_departments}

        # 验证部门关系信息
        assert self._gen_parent_relations_from_db(
            data_source=bare_local_data_source
        ) == self._gen_parent_relations_from_raw_departments(raw_departments)

    def test_update(self, data_source_sync_task_ctx, full_local_data_source):
        raw_departments = [
            RawDataSourceDepartment(code="company", name="公司", parent=None, extras={"region": "SZ"}),
            RawDataSourceDepartment(code="dept_a", name="部门A(重命名)", parent="company", extras={"region": "GZ"}),
            RawDataSourceDepartment(code="dept_c", name="部门C", parent="company", extras={"region": "SH"}),
            RawDataSourceDepartment(code="center_ca", name="中心CA", parent="dept_c", extras={"region": "CS"}),
        ]
        self._sync_data_source_departments(
            data_source_sync_task_ctx, full_local_data_source, raw_departments, overwrite=True, incremental=False
        )

        # 验证部门信息
        departments = DataSourceDepartment.objects.filter(data_source=full_local_data_source)
        assert departments.count() == len(raw_departments)
        assert set(departments.values_list("code", flat=True)) == {dept.code for dept in raw_departments}
        assert set(departments.values_list("name", flat=True)) == {dept.name for dept in raw_departments}
        assert departments.filter(code="dept_a").first().extras == {"region": "GZ"}
        assert departments.filter(code="dept_c").first().extras == {"region": "SH"}

        # 验证部门关系信息
        assert self._gen_parent_relations_from_db(
            data_source=full_local_data_source
        ) == self._gen_parent_relations_from_raw_departments(raw_departments)

    def test_update_with_incremental(self, data_source_sync_task_ctx, full_local_data_source, random_raw_department):
        dept_relation_cnt_before_sync = DataSourceDepartmentRelation.objects.filter(
            data_source=full_local_data_source
        ).count()
        excepted_dept_codes = set(
            DataSourceDepartment.objects.filter(data_source=full_local_data_source).values_list("code", flat=True)
        )
        excepted_dept_codes.add(random_raw_department.code)

        self._sync_data_source_departments(
            data_source_sync_task_ctx,
            full_local_data_source,
            [random_raw_department],
            overwrite=True,
            incremental=True,
        )

        depts = DataSourceDepartment.objects.filter(data_source=full_local_data_source)
        assert set(depts.values_list("code", flat=True)) == excepted_dept_codes
        # 随机部门只有一个父部门，所以应该会多一个关系
        assert DataSourceDepartmentRelation.objects.filter(data_source=full_local_data_source).count() == (
            dept_relation_cnt_before_sync + 1
        )

    def test_update_without_incremental_and_overwrite(
        self, data_source_sync_task_ctx, full_local_data_source, raw_departments
    ):
        with pytest.raises(ValueError, match="incremental or overwrite must be True"):
            self._sync_data_source_departments(
                data_source_sync_task_ctx, full_local_data_source, raw_departments, overwrite=False, incremental=False
            )

    def test_destroy(self, data_source_sync_task_ctx, full_local_data_source):
        raw_departments: List[RawDataSourceDepartment] = []
        self._sync_data_source_departments(
            data_source_sync_task_ctx, full_local_data_source, raw_departments, overwrite=True, incremental=False
        )

        # 同步了空的数据，导致该数据源的所有部门，部门关系信息都被删除
        assert not DataSourceDepartment.objects.filter(data_source=full_local_data_source).exists()
        assert not DataSourceDepartmentRelation.objects.filter(data_source=full_local_data_source).exists()

    @staticmethod
    def _sync_data_source_departments(
        data_source_sync_task_ctx: DataSourceSyncTaskContext,
        data_source: DataSource,
        raw_departments: List[RawDataSourceDepartment],
        overwrite: bool,
        incremental: bool,
    ):
        """执行数据源部门同步（所有步骤）"""
        kwargs = {
            "ctx": data_source_sync_task_ctx,
            "data_source": data_source,
            "raw_departments": raw_departments,
            "overwrite": overwrite,
            "incremental": incremental,
        }
        DataSourceDepartmentSyncer(**kwargs).sync()  # type: ignore
        DataSourceDepartmentRelationSyncer(**kwargs).sync()  # type: ignore

    @staticmethod
    def _gen_parent_relations_from_raw_departments(
        raw_depts: List[RawDataSourceDepartment],
    ) -> Set[Tuple[str, str | None]]:
        return {(dept.code, dept.parent) for dept in raw_depts}

    @staticmethod
    def _gen_parent_relations_from_db(data_source: DataSource) -> Set[Tuple[str, str | None]]:
        dept_relations = DataSourceDepartmentRelation.objects.filter(data_source=data_source)
        return {(rel.department.code, rel.parent.department.code if rel.parent else None) for rel in dept_relations}
