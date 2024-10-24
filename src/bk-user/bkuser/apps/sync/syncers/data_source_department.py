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

# ignore custom logger must use %s string format in this file
# ruff: noqa: G004
from typing import Dict, List, Set

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DepartmentRelationMPTTTree,
)
from bkuser.apps.sync.constants import DataSourceSyncObjectType, SyncOperation
from bkuser.apps.sync.contexts import DataSourceSyncTaskContext
from bkuser.plugins.models import RawDataSourceDepartment
from bkuser.utils.tree import bfs_traversal_tree, build_forest_with_parent_relations


class DataSourceDepartmentSyncer:
    """数据源部门同步器"""

    # 单次批量创建 / 更新数量
    batch_size = 250

    def __init__(
        self,
        ctx: DataSourceSyncTaskContext,
        data_source: DataSource,
        raw_departments: List[RawDataSourceDepartment],
        overwrite: bool,
        incremental: bool,
    ):
        # 增量模式下才可以选择覆不覆盖，全量模式下只有覆盖
        if not (incremental or overwrite):
            raise ValueError("incremental or overwrite must be True")

        self.ctx = ctx
        self.data_source = data_source
        self.raw_departments = raw_departments
        self.overwrite = overwrite
        self.incremental = incremental

    def sync(self):
        self.ctx.logger.info("start sync departments...")
        self._sync_departments()
        self.ctx.logger.info("departments sync finished")

    def _sync_departments(self):
        """数据源部门同步"""
        dept_codes = set(
            DataSourceDepartment.objects.filter(data_source=self.data_source).values_list("code", flat=True)
        )
        raw_dept_codes = {dept.code for dept in self.raw_departments}

        waiting_create_dept_codes = raw_dept_codes - dept_codes
        waiting_delete_dept_codes = dept_codes - raw_dept_codes if not self.incremental else set()
        waiting_update_dept_codes = dept_codes & raw_dept_codes if self.overwrite else set()

        waiting_delete_depts = self._get_waiting_delete_departments(waiting_delete_dept_codes)
        waiting_update_depts = self._get_waiting_update_departments(self.raw_departments, waiting_update_dept_codes)
        waiting_create_depts = self._get_waiting_create_departments(self.raw_departments, waiting_create_dept_codes)

        with transaction.atomic():
            # Q: 为什么这里的顺序应该是 1. 删除 2. 更新 3. 创建
            # A: 同步操作原则是数据库尽可能 “干净” 以避免冲突，因此删除是最优先的，可以让数据更少，
            #  而更新放在第二步的原因是 “挪窝”，可以避免一些已有的数据和待创建的数据冲突导致同步失败
            waiting_delete_depts.delete()
            DataSourceDepartment.objects.bulk_update(
                waiting_update_depts, fields=["name", "extras", "updated_at"], batch_size=self.batch_size
            )
            DataSourceDepartment.objects.bulk_create(waiting_create_depts, batch_size=self.batch_size)

        # 数据源部门同步相关日志
        self.ctx.logger.info(f"delete {len(waiting_delete_depts)} departments")
        self.ctx.recorder.add(SyncOperation.DELETE, DataSourceSyncObjectType.DEPARTMENT, waiting_delete_depts)

        self.ctx.logger.info(f"update {len(waiting_update_depts)} departments")
        self.ctx.recorder.add(SyncOperation.UPDATE, DataSourceSyncObjectType.DEPARTMENT, waiting_update_depts)

        self.ctx.logger.info(f"create {len(waiting_create_depts)} departments")
        self.ctx.recorder.add(SyncOperation.CREATE, DataSourceSyncObjectType.DEPARTMENT, waiting_create_depts)

    def _get_waiting_delete_departments(self, dept_codes: Set[str]) -> QuerySet[DataSourceDepartment]:
        return DataSourceDepartment.objects.filter(data_source=self.data_source, code__in=dept_codes)

    def _get_waiting_create_departments(
        self, raw_departments: List[RawDataSourceDepartment], waiting_create_dept_codes: Set[str]
    ) -> List[DataSourceDepartment]:
        return [
            DataSourceDepartment(data_source=self.data_source, code=dept.code, name=dept.name, extras=dept.extras)
            for dept in raw_departments
            if dept.code in waiting_create_dept_codes
        ]

    def _get_waiting_update_departments(
        self, raw_departments: List[RawDataSourceDepartment], waiting_update_dept_codes: Set[str]
    ) -> List[DataSourceDepartment]:
        if not waiting_update_dept_codes:
            return []

        dept_map = {
            dept.code: DataSourceDepartment(
                data_source=self.data_source, code=dept.code, name=dept.name, extras=dept.extras
            )
            for dept in raw_departments
            if dept.code in waiting_update_dept_codes
        }

        may_update_departments = DataSourceDepartment.objects.filter(
            data_source=self.data_source, code__in=[u.code for u in raw_departments]
        )
        waiting_update_departments = []
        for d in may_update_departments:
            target_dept = dept_map[d.code]
            # 前后数据都一致，没有更新的必要
            if d.name == target_dept.name and d.extras == target_dept.extras:
                continue

            d.name = target_dept.name
            d.extras = target_dept.extras
            d.updated_at = timezone.now()
            waiting_update_departments.append(d)

        return waiting_update_departments


class DataSourceDepartmentRelationSyncer:
    """数据源部门关系同步器"""

    # 单次批量创建 / 更新数量
    batch_size = 250

    def __init__(
        self,
        ctx: DataSourceSyncTaskContext,
        data_source: DataSource,
        raw_departments: List[RawDataSourceDepartment],
        overwrite: bool,
        incremental: bool,
    ):
        # 增量模式下才可以选择覆不覆盖，全量模式下只有覆盖
        if not (incremental or overwrite):
            raise ValueError("incremental or overwrite must be True")

        self.ctx = ctx
        self.data_source = data_source
        self.raw_departments = raw_departments
        self.overwrite = overwrite
        self.incremental = incremental

    def sync(self):
        self.ctx.logger.info("start sync department relations...")
        self._sync_department_relations()
        self.ctx.logger.info("department relations sync finished")

    def _sync_department_relations(self):
        """数据源部门关系同步"""
        # {dept_code: data_source_dept}
        dept_code_map = {dept.code: dept for dept in DataSourceDepartment.objects.filter(data_source=self.data_source)}
        # {dept_code: parent_dept_code}
        dept_parent_code_map = {dept.code: dept.parent for dept in self.raw_departments}

        # 如果是增量同步模式，则需要将存量的部门关系捞出来，和新的合并下，再删除重建
        # Q: 为什么不是增量模式时候，一通对比之后，直接往现有的 MPTT 森林里面塞节点？
        # A: MPTT 树结构复杂，变更操作可能存在风险，且后台任务对性能要求不高，先用简单的删除重建方案
        if self.incremental:
            for relation in DataSourceDepartmentRelation.objects.filter(data_source=self.data_source):
                # 如果某个部门有新的父部门，则跳过
                if relation.department.code in dept_parent_code_map:
                    continue

                dept_parent_code_map[relation.department.code] = (
                    relation.parent.department.code if relation.parent else None
                )

        # {dept_code: data_source_dept_relation}
        dept_code_rel_map: Dict[str, DataSourceDepartmentRelation] = {}
        mptt_tree_ids: Set[int] = set()

        parent_relations = list(dept_parent_code_map.items())
        # 根据部门父子关系，构建森林
        forest_roots = build_forest_with_parent_relations(parent_relations)
        # 逐棵树进行便利，因为需要保证一棵树的节点拥有相同的 tree_id
        for root in forest_roots:
            tree_id = self._generate_tree_id(self.data_source)
            mptt_tree_ids.add(tree_id)

            # 通过 bfs 遍历的方式，确保父节点会先被创建
            for node in bfs_traversal_tree(root):
                parent_code = dept_parent_code_map.get(node.id)
                if not parent_code:
                    parent = None
                else:
                    parent = dept_code_rel_map.get(parent_code)

                dept_code_rel_map[node.id] = DataSourceDepartmentRelation(
                    data_source=self.data_source,
                    department=dept_code_map[node.id],
                    parent=parent,
                    tree_id=tree_id,
                    # NOTE：初始化时 lft, rght, level 均不能为空，
                    # 因此先赋零值，后面 partial_rebuild 会修改
                    lft=0,
                    rght=0,
                    level=0,
                )

        with DataSourceDepartmentRelation.objects.disable_mptt_updates(), transaction.atomic():
            # 对于部门关系边，先先全部删除
            DataSourceDepartmentRelation.objects.filter(data_source=self.data_source).delete()
            # 最后再全部批量创建
            DataSourceDepartmentRelation.objects.bulk_create(
                list(dept_code_rel_map.values()), batch_size=self.batch_size
            )
            # 逐棵对当前数据源的树进行重建
            for tree_id in mptt_tree_ids:
                DataSourceDepartmentRelation.objects.partial_rebuild(tree_id)

        self.ctx.logger.info(f"re-create {len(dept_code_rel_map)} department relations")
        self.ctx.logger.info(f"data source has {len(mptt_tree_ids)} department tree(s) currently")

    @staticmethod
    def _generate_tree_id(data_source: DataSource) -> int:
        """
        在 MPTT 中，单个 tree_id 只能用于一棵树，因此需要为不同的树分配不同的 ID

        分配实现：利用 MySQL 自增 ID 分配 tree_id（不需要包含到事务中，虽然可能造成浪费）
        """
        return DepartmentRelationMPTTTree.objects.create(data_source=data_source).id
