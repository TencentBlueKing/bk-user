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
import datetime
from typing import Dict, List, Set

from django.utils import timezone

from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
    DepartmentRelationMPTTTree,
)
from bkuser.apps.sync.constants import DataSourceSyncObjectType, SyncOperation, TenantSyncObjectType
from bkuser.apps.sync.context import DataSourceSyncTaskContext, TenantSyncTaskContext
from bkuser.apps.sync.converters import DataSourceUserConverter
from bkuser.apps.tenant.models import Tenant, TenantDepartment, TenantUser
from bkuser.common.constants import PERMANENT_TIME
from bkuser.plugins.models import RawDataSourceDepartment, RawDataSourceUser
from bkuser.utils.tree import bfs_traversal_tree, build_forest_with_parent_relations
from bkuser.utils.uuid import generate_uuid


class DataSourceDepartmentSyncer:
    """数据源部门同步器"""

    # 单次批量创建 / 更新数量
    batch_size = 250

    def __init__(
        self,
        ctx: DataSourceSyncTaskContext,
        data_source: DataSource,
        raw_departments: List[RawDataSourceDepartment],
    ):
        self.ctx = ctx
        self.data_source = data_source
        self.raw_departments = raw_departments

    def sync(self):
        self.ctx.logger.info(f"receive {len(self.raw_departments)} departments from data source plugin")  # noqa: G004

        self.ctx.logger.info("start sync departments...")
        self._sync_departments()
        self.ctx.logger.info("departments sync finished")

        self.ctx.logger.info("start sync department relations...")
        self._sync_department_relations()
        self.ctx.logger.info("department relations sync finished")

    def _sync_departments(self):
        """数据源部门同步"""
        dept_codes = set(
            DataSourceDepartment.objects.filter(data_source=self.data_source).values_list("code", flat=True)
        )
        raw_dept_codes = {dept.code for dept in self.raw_departments}

        waiting_create_dept_codes = raw_dept_codes - dept_codes
        waiting_delete_dept_codes = dept_codes - raw_dept_codes
        waiting_update_dept_codes = dept_codes & raw_dept_codes

        if waiting_delete_dept_codes:
            self._delete_departments(waiting_delete_dept_codes)

        if waiting_create_dept_codes:
            self._create_departments([u for u in self.raw_departments if u.code in waiting_create_dept_codes])

        if waiting_update_dept_codes:
            self._update_departments([u for u in self.raw_departments if u.code in waiting_update_dept_codes])

    def _delete_departments(self, dept_codes: Set[str]):
        waiting_delete_depts = DataSourceDepartment.objects.filter(data_source=self.data_source, code__in=dept_codes)

        self.ctx.logger.info(f"delete {len(waiting_delete_depts)} departments")  # noqa: G004
        self.ctx.recorder.add(SyncOperation.DELETE, DataSourceSyncObjectType.DEPARTMENT, waiting_delete_depts)

        waiting_delete_depts.delete()

    def _create_departments(self, raw_departments: List[RawDataSourceDepartment]):
        departments = [
            DataSourceDepartment(data_source=self.data_source, code=dept.code, name=dept.name)
            for dept in raw_departments
        ]
        DataSourceDepartment.objects.bulk_create(departments, batch_size=self.batch_size)

        self.ctx.logger.info(f"create {len(departments)} departments")  # noqa: G004
        self.ctx.recorder.add(SyncOperation.CREATE, DataSourceSyncObjectType.DEPARTMENT, departments)

    def _update_departments(self, raw_departments: List[RawDataSourceDepartment]):
        dept_map = {
            dept.code: DataSourceDepartment(data_source=self.data_source, code=dept.code, name=dept.name)
            for dept in raw_departments
        }

        may_update_departments = DataSourceDepartment.objects.filter(
            data_source=self.data_source, code__in=[u.code for u in raw_departments]
        )
        waiting_update_departments = []
        for d in may_update_departments:
            target_dept = dept_map[d.code]
            if d.name == target_dept.name:
                continue

            d.name = target_dept.name
            d.updated_at = timezone.now()
            waiting_update_departments.append(d)

        if not waiting_update_departments:
            return

        DataSourceDepartment.objects.bulk_update(
            waiting_update_departments, fields=["name", "updated_at"], batch_size=self.batch_size
        )
        self.ctx.logger.info(f"update {len(waiting_update_departments)} departments")  # noqa: G004
        self.ctx.recorder.add(SyncOperation.UPDATE, DataSourceSyncObjectType.DEPARTMENT, waiting_update_departments)

    def _sync_department_relations(self):
        """数据源部门关系同步"""
        # {dept_code: data_source_dept}
        dept_code_map = {dept.code: dept for dept in DataSourceDepartment.objects.filter(data_source=self.data_source)}
        # {dept_code: parent_dept_code}
        dept_parent_code_map = {dept.code: dept.parent for dept in self.raw_departments}
        # {dept_code: data_source_dept_relation}
        dept_code_rel_map: Dict[str, DataSourceDepartmentRelation] = {}

        # 目前采用全部删除，再重建的方式
        mptt_tree_ids = set()
        with DataSourceDepartmentRelation.objects.disable_mptt_updates():
            DataSourceDepartmentRelation.objects.filter(data_source=self.data_source).delete()
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

            # 最后再全部批量创建
            DataSourceDepartmentRelation.objects.bulk_create(
                list(dept_code_rel_map.values()), batch_size=self.batch_size
            )

        self.ctx.logger.info(f"re-create {len(dept_code_rel_map)} department relations")  # noqa: G004
        self.ctx.logger.info(f"data source has {len(mptt_tree_ids)} department tree(s) currently")  # noqa: G004

        # 逐棵对当前数据源的树进行重建
        for tree_id in mptt_tree_ids:
            DataSourceDepartmentRelation.objects.partial_rebuild(tree_id)

    @staticmethod
    def _generate_tree_id(data_source: DataSource) -> int:
        """
        在 MPTT 中，单个 tree_id 只能用于一棵树，因此需要为不同的树分配不同的 ID

        分配实现：利用 MySQL 自增 ID 分配 tree_id
        """
        return DepartmentRelationMPTTTree.objects.create(data_source=data_source).id


class DataSourceUserSyncer:
    """数据源用户同步器，支持覆盖更新，日志记录等"""

    # 单次批量创建 / 更新数量
    batch_size = 250

    def __init__(
        self,
        ctx: DataSourceSyncTaskContext,
        data_source: DataSource,
        raw_users: List[RawDataSourceUser],
        overwrite: bool = False,
        incremental: bool = False,
    ):
        self.ctx = ctx
        self.data_source = data_source
        self.raw_users = raw_users
        self.overwrite = overwrite
        self.incremental = incremental
        self.converter = DataSourceUserConverter(data_source, ctx.logger)

    def sync(self):
        self.ctx.logger.info(f"receive {len(self.raw_users)} users from data source plugin")  # noqa: G004
        self._validate_users()

        self.ctx.logger.info("start sync users...")
        self._sync_users()
        self.ctx.logger.info("users sync finished")

        self.ctx.logger.info("start sync user-leader relations...")
        self._sync_user_leader_relations()
        self.ctx.logger.info("user-leader relations sync finished")

        self.ctx.logger.info("start sync user-department relations...")
        self._sync_user_department_relations()
        self.ctx.logger.info("user-department relations sync finished")

    def _validate_users(self):
        """对用户数据进行校验（插件提供的数据不一定是合法的）"""
        exists_user_codes = set(
            DataSourceUser.objects.filter(data_source=self.data_source).values_list("code", flat=True)
        )

        # 检查本次同步的用户数据中，所有的 leader 是否已经存在
        raw_leader_codes = {leader_code for user in self.raw_users for leader_code in user.leaders}

        user_codes = {user.code for user in self.raw_users}
        # 如果是增量同步，则 DB 中已经存在的用户，也可以作为 leader
        if self.incremental:
            user_codes |= exists_user_codes

        # Q: 提示信息使用 user_code 是否影响可读性
        # A：本地数据源用户 code 即为用户名，因此不会有可读性问题
        #  非本地数据源，因为本身插件提供的用户 Leader 信息即 code 列表，因此是可映射回实际数据的
        if not_exists_leaders := raw_leader_codes - user_codes:
            self.ctx.logger.warning(
                "user leader: {} is missing, this may skip some user-leader relations from being created.".format(  # noqa: G001, E501
                    ", ".join(not_exists_leaders)
                )
            )

        # 数据源部门会先于用户同步，因此这里取到的就是所有可用的数据源部门 code
        exists_dept_codes = set(
            DataSourceDepartment.objects.filter(data_source=self.data_source).values_list("code", flat=True)
        )
        raw_user_dept_codes = {dept_code for user in self.raw_users for dept_code in user.departments}
        # 需要确保待同步的 用户-部门 关系中的部门都是存在的
        # Q: 提示信息使用 dept_code 是否影响可读性
        # A：尽管本地数据源使用 Hash 值作为部门 code，但是组织路径中的部门都会被创建，理论上不会触发该处异常
        #  非本地数据源，因为本身插件提供的用户部门信息即 code 列表，因此是可映射回实际的部门数据的
        if not_exists_depts := raw_user_dept_codes - exists_dept_codes:
            self.ctx.logger.warning(
                "user department: {} is missing, this may skip some user-dept relations from being created.".format(  # noqa: G001, E501
                    ", ".join(not_exists_depts)
                )
            )

    def _sync_users(self):
        user_codes = set(DataSourceUser.objects.filter(data_source=self.data_source).values_list("code", flat=True))
        raw_user_codes = {user.code for user in self.raw_users}

        waiting_create_user_codes = raw_user_codes - user_codes
        waiting_delete_user_codes = user_codes - raw_user_codes if not self.incremental else set()
        waiting_update_user_codes = user_codes & raw_user_codes if self.overwrite else set()

        if waiting_delete_user_codes:
            self._delete_users(waiting_delete_user_codes)

        if waiting_create_user_codes:
            self._create_users([u for u in self.raw_users if u.code in waiting_create_user_codes])

        if waiting_update_user_codes:
            self._update_users([u for u in self.raw_users if u.code in waiting_update_user_codes])

    def _delete_users(self, user_codes: Set[str]):
        waiting_delete_users = DataSourceUser.objects.filter(data_source=self.data_source, code__in=user_codes)

        self.ctx.logger.info(f"delete {len(waiting_delete_users)} users")  # noqa: G004
        self.ctx.recorder.add(SyncOperation.DELETE, DataSourceSyncObjectType.USER, waiting_delete_users)

        waiting_delete_users.delete()

    def _create_users(self, raw_users: List[RawDataSourceUser]):
        users = [self.converter.convert(u) for u in raw_users]
        DataSourceUser.objects.bulk_create(users, batch_size=self.batch_size)

        self.ctx.logger.info(f"create {len(users)} users")  # noqa: G004
        self.ctx.recorder.add(SyncOperation.CREATE, DataSourceSyncObjectType.USER, users)

    def _update_users(self, raw_users: List[RawDataSourceUser]):
        user_map = {u.code: self.converter.convert(u) for u in raw_users}

        may_update_users = DataSourceUser.objects.filter(
            data_source=self.data_source, code__in=[u.code for u in raw_users]
        )
        waiting_update_users = []
        for u in may_update_users:
            # 先进行 diff，不是所有的用户都要被更新，只有有字段不一致的，才需要更新
            target_user = user_map[u.code]
            if (
                # u.username == target_user.username
                u.full_name == target_user.full_name
                and u.email == target_user.email
                and u.phone == target_user.phone
                and u.phone_country_code == target_user.phone_country_code
                and u.extras == target_user.extras
            ):
                continue

            # FIXME (su) 评估 username 更新策略 https://github.com/TencentBlueKing/bk-user/issues/1325
            # u.username = target_user.username
            u.full_name = target_user.full_name
            u.email = target_user.email
            u.phone = target_user.phone
            u.phone_country_code = target_user.phone_country_code
            u.extras = target_user.extras
            u.updated_at = timezone.now()
            # 真正需要更新的用户，是有字段不一致的
            waiting_update_users.append(u)

        if not waiting_update_users:
            return

        DataSourceUser.objects.bulk_update(
            waiting_update_users,
            fields=["username", "full_name", "email", "phone", "phone_country_code", "extras", "updated_at"],
            batch_size=self.batch_size,
        )
        self.ctx.logger.info(f"update {len(waiting_update_users)} users")  # noqa: G004
        self.ctx.recorder.add(SyncOperation.UPDATE, DataSourceSyncObjectType.USER, waiting_update_users)

    def _sync_user_leader_relations(self):
        """同步用户 Leader 关系"""
        exists_users = DataSourceUser.objects.filter(data_source=self.data_source)
        # 此时已经完成了用户数据的同步，可以认为 DB 中 DataSourceUser 的数据是最新的，准确的
        user_code_id_map = {u.code: u.id for u in exists_users}
        # 最终需要的 [(user_code, leader_code)] 集合
        user_leader_code_tuples = {(u.code, leader_code) for u in self.raw_users for leader_code in u.leaders}
        # 最终需要的 [(user_id, leader_id)] 集合，需要注意的是：
        # 由于可能有数据指定了不存在的 leader（有警告日志），因此需要先判断下
        user_leader_id_tuples = {
            (user_code_id_map[user_code], user_code_id_map[leader_code])
            for (user_code, leader_code) in user_leader_code_tuples
            if user_code in user_code_id_map and leader_code in user_code_id_map
        }

        # 现有 DB 中的数据捞出来，组成 {(user_id, leader_id): relation_id} 映射表
        exists_user_leader_relations_map = {
            (rel.user_id, rel.leader_id): rel.id
            for rel in DataSourceUserLeaderRelation.objects.filter(data_source=self.data_source)
        }
        exists_user_leader_id_tuples = set(exists_user_leader_relations_map.keys())

        # 集合做差，再转换 ID，生成需要创建的 Relations
        if waiting_create_user_leader_id_tuples := user_leader_id_tuples - exists_user_leader_id_tuples:
            waiting_create_user_leader_relations = [
                # NOTE 外键对象也可以直接指定 id 进行初始化
                DataSourceUserLeaderRelation(user_id=user_id, leader_id=leader_id, data_source=self.data_source)
                for (user_id, leader_id) in waiting_create_user_leader_id_tuples
            ]
            DataSourceUserLeaderRelation.objects.bulk_create(
                waiting_create_user_leader_relations, batch_size=self.batch_size
            )
            # 记录 用户-直接上级 关系新增日志
            self.ctx.logger.info(
                f"create {len(waiting_create_user_leader_relations)} user-leader relations"  # noqa: G004
            )

        # 集合做差，再转换成 relation ID，得到需要删除的 relation ID 列表
        if waiting_delete_user_leader_id_tuples := exists_user_leader_id_tuples - user_leader_id_tuples:
            waiting_delete_user_leader_relation_ids = [
                exists_user_leader_relations_map[t] for t in waiting_delete_user_leader_id_tuples
            ]
            DataSourceUserLeaderRelation.objects.filter(id__in=waiting_delete_user_leader_relation_ids).delete()
            # 记录 用户-直接上级 关系删除日志
            self.ctx.logger.info(
                f"delete {len(waiting_delete_user_leader_relation_ids)} user-leader relations"  # noqa: G004
            )

    def _sync_user_department_relations(self):
        """同步用户部门关系"""
        exists_users = DataSourceUser.objects.filter(data_source=self.data_source)
        # 此时已经完成了用户，部门数据的同步，可以认为 DB 中 DataSourceUser & Department 的数据是最新的，准确的
        user_code_id_map = {u.code: u.id for u in exists_users}
        department_code_id_map = {
            d.code: d.id for d in DataSourceDepartment.objects.filter(data_source=self.data_source)
        }

        # 最终需要的 [(user_code, dept_code)] 集合
        user_dept_code_tuples = {(u.code, dept_code) for u in self.raw_users for dept_code in u.departments}
        # 最终需要的 [(user_id, dept_id)] 集合，需要注意的是：
        # 由于可能有数据指定了不存在的部门（有警告日志），因此需要先判断下
        user_dept_id_tuples = {
            (user_code_id_map[user_code], department_code_id_map[dept_code])
            for (user_code, dept_code) in user_dept_code_tuples
            if user_code in user_code_id_map and dept_code in department_code_id_map
        }

        # 现有 DB 中的数据捞出来，组成 {(user_id, dept_id): relation_id} 映射表
        exists_user_dept_relations_map = {
            (rel.user_id, rel.department_id): rel.id
            for rel in DataSourceDepartmentUserRelation.objects.filter(data_source=self.data_source)
        }
        exists_user_dept_id_tuples = set(exists_user_dept_relations_map.keys())

        # 集合做差，再转换 ID，生成需要创建的 Relations
        if waiting_create_user_dept_id_tuples := user_dept_id_tuples - exists_user_dept_id_tuples:
            waiting_create_user_dept_relations = [
                # NOTE 外键对象也可以直接指定 id 进行初始化
                DataSourceDepartmentUserRelation(user_id=user_id, department_id=dept_id, data_source=self.data_source)
                for (user_id, dept_id) in waiting_create_user_dept_id_tuples
            ]
            DataSourceDepartmentUserRelation.objects.bulk_create(
                waiting_create_user_dept_relations, batch_size=self.batch_size
            )
            # 记录 用户-部门 关系新增日志
            self.ctx.logger.info(
                f"create {len(waiting_create_user_dept_relations)} user-department relations"  # noqa: G004
            )

        # 集合做差，再转换成 relation ID，得到需要删除的 relation ID 列表
        if waiting_delete_user_dept_id_tuples := exists_user_dept_id_tuples - user_dept_id_tuples:
            waiting_delete_user_dept_relation_ids = [
                exists_user_dept_relations_map[t] for t in waiting_delete_user_dept_id_tuples
            ]
            DataSourceDepartmentUserRelation.objects.filter(id__in=waiting_delete_user_dept_relation_ids).delete()
            # 记录 用户-部门 关系删除日志
            self.ctx.logger.info(
                f"delete {len(waiting_delete_user_dept_relation_ids)} user-department relations"  # noqa: G004
            )


class TenantDepartmentSyncer:
    """租户部门同步器"""

    batch_size = 250

    def __init__(self, ctx: TenantSyncTaskContext, data_source: DataSource, tenant: Tenant):
        self.ctx = ctx
        self.data_source = data_source
        self.tenant = tenant

    def sync(self):
        """TODO (su) 支持协同后，同步到租户的数据有范围限制"""
        exists_tenant_departments = TenantDepartment.objects.filter(tenant=self.tenant, data_source=self.data_source)
        data_source_departments = DataSourceDepartment.objects.filter(data_source=self.data_source)

        # 删除掉租户中存在的，但是数据源中不存在的
        waiting_delete_tenant_departments = exists_tenant_departments.exclude(
            data_source_department__in=data_source_departments
        )
        # 记录删除日志，变更记录
        waiting_delete_cnt = len(waiting_delete_tenant_departments)
        self.ctx.logger.info(f"delete {waiting_delete_cnt} tenant departments")  # noqa: G004
        self.ctx.recorder.add(SyncOperation.DELETE, TenantSyncObjectType.DEPARTMENT, waiting_delete_tenant_departments)

        waiting_delete_tenant_departments.delete()

        # 数据源中存在，但是租户中不存在的，需要创建
        waiting_sync_data_source_departments = data_source_departments.exclude(
            id__in=[u.data_source_department_id for u in exists_tenant_departments]
        )
        waiting_create_tenant_departments = [
            TenantDepartment(
                tenant=self.tenant,
                data_source_department=dept,
                data_source=self.data_source,
            )
            for dept in waiting_sync_data_source_departments
        ]
        TenantDepartment.objects.bulk_create(waiting_create_tenant_departments, batch_size=self.batch_size)

        # 记录创建日志，变更记录
        waiting_create_cnt = len(waiting_create_tenant_departments)
        self.ctx.logger.info(f"create {waiting_create_cnt} tenant departments")  # noqa: G004
        self.ctx.recorder.add(SyncOperation.CREATE, TenantSyncObjectType.DEPARTMENT, waiting_create_tenant_departments)


class TenantUserSyncer:
    """租户部门同步器"""

    batch_size = 250

    def __init__(self, ctx: TenantSyncTaskContext, data_source: DataSource, tenant: Tenant):
        self.ctx = ctx
        self.data_source = data_source
        self.tenant = tenant
        self.user_account_expired_at = self._get_user_account_expired_at()

    def sync(self):
        """TODO (su) 支持协同后，同步到租户的数据有范围限制"""
        exists_tenant_users = TenantUser.objects.filter(tenant=self.tenant, data_source=self.data_source)
        data_source_users = DataSourceUser.objects.filter(data_source=self.data_source)

        # 删除掉租户中存在的，但是数据源中不存在的
        waiting_delete_tenant_users = exists_tenant_users.exclude(data_source_user__in=data_source_users)

        # 记录删除日志，变更记录
        self.ctx.logger.info(f"delete {len(waiting_delete_tenant_users)} tenant users")  # noqa: G004
        self.ctx.recorder.add(SyncOperation.DELETE, TenantSyncObjectType.USER, waiting_delete_tenant_users)

        waiting_delete_tenant_users.delete()

        # 数据源中存在，但是租户中不存在的，需要创建
        waiting_sync_data_source_users = data_source_users.exclude(
            id__in=[u.data_source_user_id for u in exists_tenant_users]
        )
        waiting_create_tenant_users = [
            TenantUser(
                id=generate_uuid(),
                tenant=self.tenant,
                data_source_user=user,
                data_source=self.data_source,
                account_expired_at=self.user_account_expired_at,
            )
            for user in waiting_sync_data_source_users
        ]
        TenantUser.objects.bulk_create(waiting_create_tenant_users, batch_size=self.batch_size)

        # 记录创建日志，变更记录
        self.ctx.logger.info(f"create {len(waiting_create_tenant_users)} tenant users")  # noqa: G004
        self.ctx.recorder.add(SyncOperation.CREATE, TenantSyncObjectType.USER, waiting_create_tenant_users)

    def _get_user_account_expired_at(self) -> datetime.datetime:
        """FIXME (su) 支持读取账号有效期配置，然后累加到 timezone.now() 上，目前是直接返回 PERMANENT_TIME"""
        return PERMANENT_TIME
