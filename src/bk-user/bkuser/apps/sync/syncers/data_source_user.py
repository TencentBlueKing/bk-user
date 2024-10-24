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
# ruff: noqa: G003, G004
from typing import Dict, List, Set, Tuple

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.sync.constants import DataSourceSyncObjectType, SyncOperation
from bkuser.apps.sync.contexts import DataSourceSyncTaskContext
from bkuser.apps.sync.converters import DataSourceUserConverter
from bkuser.apps.tenant.utils import is_username_frozen
from bkuser.plugins.models import RawDataSourceUser


class DataSourceUserSyncer:
    """数据源用户同步器，支持覆盖更新，日志记录等"""

    # 单次批量创建 / 更新数量
    batch_size = 250

    def __init__(
        self,
        ctx: DataSourceSyncTaskContext,
        data_source: DataSource,
        raw_users: List[RawDataSourceUser],
        overwrite: bool,
        incremental: bool,
    ):
        # 增量模式下才可以选择覆不覆盖，全量模式下只有覆盖
        if not (incremental or overwrite):
            raise ValueError("incremental or overwrite must be True")

        self.ctx = ctx
        self.data_source = data_source
        self.raw_users = raw_users
        self.overwrite = overwrite
        self.incremental = incremental
        self.converter = DataSourceUserConverter(data_source, ctx.logger)
        # 由于在部分老版本迁移过来的数据源中租户用户 ID 会由 username + 规则 拼接生成，
        # 该类数据源同步时候不可更新 username，而全新数据源对应租户 ID 都是 uuid 则不受影响
        self.enable_update_username = not is_username_frozen(data_source)

    def sync(self):
        self.ctx.logger.info("start sync users...")
        self._sync_users()
        self.ctx.logger.info("users sync finished")

    def _sync_users(self):
        user_codes = set(DataSourceUser.objects.filter(data_source=self.data_source).values_list("code", flat=True))
        raw_user_codes = {user.code for user in self.raw_users}

        waiting_create_user_codes = raw_user_codes - user_codes
        waiting_delete_user_codes = user_codes - raw_user_codes if not self.incremental else set()
        waiting_update_user_codes = user_codes & raw_user_codes if self.overwrite else set()

        waiting_delete_users = self._get_waiting_delete_users(waiting_delete_user_codes)
        waiting_update_users = self._get_waiting_update_users(self.raw_users, waiting_update_user_codes)
        waiting_create_users = self._get_waiting_create_users(self.raw_users, waiting_create_user_codes)

        with transaction.atomic():
            # Q: 为什么这里的顺序应该是 1. 删除 2. 更新 3. 创建
            # A: 同步操作原则是数据库尽可能 “干净” 以避免冲突，因此删除是最优先的，可以让数据更少，
            #  而更新放在第二步的原因是 “挪窝”，可以避免一些已有的数据和待创建的数据冲突导致同步失败
            waiting_delete_users.delete()
            DataSourceUser.objects.bulk_update(
                waiting_update_users,
                fields=["username", "full_name", "email", "phone", "phone_country_code", "extras", "updated_at"],
                batch_size=self.batch_size,
            )
            DataSourceUser.objects.bulk_create(waiting_create_users, batch_size=self.batch_size)

        self.ctx.logger.info(f"delete {len(waiting_delete_users)} users")
        self.ctx.recorder.add(SyncOperation.DELETE, DataSourceSyncObjectType.USER, waiting_delete_users)

        self.ctx.logger.info(f"update {len(waiting_update_users)} users")
        self.ctx.recorder.add(SyncOperation.UPDATE, DataSourceSyncObjectType.USER, waiting_update_users)

        self.ctx.logger.info(f"create {len(waiting_create_users)} users")
        self.ctx.recorder.add(SyncOperation.CREATE, DataSourceSyncObjectType.USER, waiting_create_users)

    def _get_waiting_delete_users(self, user_codes: Set[str]) -> QuerySet[DataSourceUser]:
        return DataSourceUser.objects.filter(data_source=self.data_source, code__in=user_codes)

    def _get_waiting_create_users(
        self, raw_users: List[RawDataSourceUser], waiting_create_user_codes: Set[str]
    ) -> List[DataSourceUser]:
        return [self.converter.convert(u) for u in raw_users if u.code in waiting_create_user_codes]

    def _get_waiting_update_users(
        self, raw_users: List[RawDataSourceUser], waiting_update_user_codes: Set[str]
    ) -> List[DataSourceUser]:
        if not waiting_update_user_codes:
            return []

        user_map = {u.code: self.converter.convert(u) for u in raw_users}

        may_update_users = DataSourceUser.objects.filter(
            data_source=self.data_source, code__in=[u.code for u in raw_users]
        )
        waiting_update_users = []
        for u in may_update_users:
            # 先进行 diff，不是所有的用户都要被更新，只有有字段不一致的，才需要更新
            target_user = user_map[u.code]
            if (
                (u.username == target_user.username or not self.enable_update_username)
                and u.full_name == target_user.full_name
                and u.email == target_user.email
                and u.phone == target_user.phone
                and u.phone_country_code == target_user.phone_country_code
                and u.extras == target_user.extras
            ):
                continue

            if self.enable_update_username:
                u.username = target_user.username

            u.full_name = target_user.full_name
            u.email = target_user.email
            u.phone = target_user.phone
            u.phone_country_code = target_user.phone_country_code
            u.extras = target_user.extras
            u.updated_at = timezone.now()
            # 真正需要更新的用户，是有字段不一致的
            waiting_update_users.append(u)

        return waiting_update_users


class DataSourceUserLeaderRelationSyncer:
    """数据源用户 - 直接上级关系同步器，支持覆盖更新，日志记录等"""

    # 单次批量创建 / 更新数量
    batch_size = 250

    def __init__(
        self,
        ctx: DataSourceSyncTaskContext,
        data_source: DataSource,
        raw_users: List[RawDataSourceUser],
        exists_user_ids_before_sync: Set[int],
        overwrite: bool,
        incremental: bool,
    ):
        # 增量模式下才可以选择覆不覆盖，全量模式下只有覆盖
        if not (incremental or overwrite):
            raise ValueError("incremental or overwrite must be True")

        self.ctx = ctx
        self.data_source = data_source
        self.raw_users = raw_users
        self.exists_user_ids_before_sync = exists_user_ids_before_sync
        self.overwrite = overwrite
        self.incremental = incremental

    def sync(self):
        self._validate_users()

        self.ctx.logger.info("start sync user-leader relations...")
        self._sync_relations()
        self.ctx.logger.info("user-leader relations sync finished")

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
                f"user leader: {', '.join(not_exists_leaders)} is missing, "
                + "this may skip some user-leader relations from being created."
            )

    def _sync_relations(self):
        """同步用户 - 直接上级关系"""
        # 此时已经完成了用户数据的同步，可以认为 DB 中 DataSourceUser 的数据是最新的，准确的
        user_code_id_map: Dict[str, int] = dict(
            DataSourceUser.objects.filter(data_source=self.data_source).values_list("code", "id")
        )
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
        exists_user_leader_relation_map = {
            (rel.user_id, rel.leader_id): rel.id
            for rel in DataSourceUserLeaderRelation.objects.filter(data_source=self.data_source)
        }
        exists_user_leader_id_tuples = set(exists_user_leader_relation_map.keys())

        # 计算待变更的关联边
        waiting_create_user_leader_relations = self._get_waiting_create_user_leader_relations(
            user_leader_id_tuples, exists_user_leader_id_tuples
        )
        waiting_delete_user_leader_relation_ids = self._get_waiting_delete_user_leader_relation_ids(
            user_code_id_map, exists_user_leader_relation_map, user_leader_id_tuples, exists_user_leader_id_tuples
        )
        # 在事务中执行对关联边的变更
        with transaction.atomic():
            if waiting_create_user_leader_relations:
                DataSourceUserLeaderRelation.objects.bulk_create(
                    waiting_create_user_leader_relations, batch_size=self.batch_size
                )
            if waiting_delete_user_leader_relation_ids:
                DataSourceUserLeaderRelation.objects.filter(id__in=waiting_delete_user_leader_relation_ids).delete()

        # 记录 用户-直接上级 关系新增日志
        self.ctx.logger.info(f"create {len(waiting_create_user_leader_relations)} user-leader relations")
        # 记录 用户-直接上级 关系删除日志
        self.ctx.logger.info(f"delete {len(waiting_delete_user_leader_relation_ids)} user-leader relations")

    def _get_waiting_create_user_leader_relations(
        self,
        user_leader_id_tuples: Set[Tuple[int, int]],
        exists_user_leader_id_tuples: Set[Tuple[int, int]],
    ) -> List[DataSourceUserLeaderRelation]:
        # 集合做差，再转换 ID，生成需要创建的 Relations
        waiting_create_user_leader_id_tuples = user_leader_id_tuples - exists_user_leader_id_tuples

        # 如果是不覆盖的场景，则同步前存量的用户，不需要追加关联边
        if not self.overwrite:
            waiting_create_user_leader_id_tuples = {
                (user_id, leader_id)
                for (user_id, leader_id) in waiting_create_user_leader_id_tuples
                if user_id not in self.exists_user_ids_before_sync
            }

        return [
            # NOTE 外键对象也可以直接指定 id 进行初始化
            DataSourceUserLeaderRelation(user_id=user_id, leader_id=leader_id, data_source=self.data_source)
            for (user_id, leader_id) in waiting_create_user_leader_id_tuples
        ]

    def _get_waiting_delete_user_leader_relation_ids(
        self,
        user_code_id_map: Dict[str, int],
        exists_user_leader_relation_map: Dict[Tuple[int, int], int],
        user_leader_id_tuples: Set[Tuple[int, int]],
        exists_user_leader_id_tuples: Set[Tuple[int, int]],
    ) -> List[int]:
        # 集合做差，再转换成 relation ID，得到需要删除的 relation ID 列表
        # 全量模式，没有覆不覆盖一说，就是覆盖，不需要特殊判断
        waiting_delete_user_leader_id_tuples = exists_user_leader_id_tuples - user_leader_id_tuples
        if self.incremental:
            # 增量模式，覆盖，则有新边的用户，老边需要被删除，其他用户关系边不变
            if self.overwrite:
                # 如果指定 leader 为空，也算是修改了关联边，在覆盖的模式下，需要清理掉旧的数据
                just_update_relation_user_ids = {user_code_id_map[user.code] for user in self.raw_users}
                waiting_delete_user_leader_id_tuples = {
                    (user_id, leader_id)
                    for user_id, leader_id in waiting_delete_user_leader_id_tuples
                    if user_id in just_update_relation_user_ids
                }
            # 增量模式，不覆盖，则直接追加即可，不要删除任何关系边
            else:
                waiting_delete_user_leader_id_tuples = set()

        return [exists_user_leader_relation_map[t] for t in waiting_delete_user_leader_id_tuples]


class DataSourceUserDeptRelationSyncer:
    """数据源用户 - 部门关系同步器，支持覆盖更新，日志记录等"""

    # 单次批量创建 / 更新数量
    batch_size = 250

    def __init__(
        self,
        ctx: DataSourceSyncTaskContext,
        data_source: DataSource,
        raw_users: List[RawDataSourceUser],
        exists_user_ids_before_sync: Set[int],
        overwrite: bool,
        incremental: bool,
    ):
        # 增量模式下才可以选择覆不覆盖，全量模式下只有覆盖
        if not (incremental or overwrite):
            raise ValueError("incremental or overwrite must be True")

        self.ctx = ctx
        self.data_source = data_source
        self.raw_users = raw_users
        self.exists_user_ids_before_sync = exists_user_ids_before_sync
        self.overwrite = overwrite
        self.incremental = incremental

    def sync(self):
        self._validate_users()

        self.ctx.logger.info("start sync user-department relations...")
        self._sync_relations()
        self.ctx.logger.info("user-department relations sync finished")

    def _validate_users(self):
        """对用户数据进行校验（插件提供的数据不一定是合法的）"""

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
                f"user department: {', '.join(not_exists_depts)} is missing, "
                + "this may skip some user-dept relations from being created."
            )

    def _sync_relations(self):
        """同步用户 - 部门关系"""
        # 此时已经完成了用户，部门数据的同步，可以认为 DB 中 DataSourceUser & Department 的数据是最新的，准确的
        user_code_id_map: Dict[str, int] = dict(
            DataSourceUser.objects.filter(data_source=self.data_source).values_list("code", "id")
        )
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

        # 计算待变更的关联边
        waiting_create_user_dept_relations = self._get_waiting_create_user_dept_relations(
            user_dept_id_tuples, exists_user_dept_id_tuples
        )
        waiting_delete_user_dept_relation_ids = self._get_waiting_delete_user_dept_relation_ids(
            user_code_id_map, exists_user_dept_relations_map, user_dept_id_tuples, exists_user_dept_id_tuples
        )

        # 在事务中执行对关联边的变更
        with transaction.atomic():
            if waiting_create_user_dept_relations:
                DataSourceDepartmentUserRelation.objects.bulk_create(
                    waiting_create_user_dept_relations, batch_size=self.batch_size
                )
            if waiting_delete_user_dept_relation_ids:
                DataSourceDepartmentUserRelation.objects.filter(id__in=waiting_delete_user_dept_relation_ids).delete()

        # 记录 用户-部门 关系新增日志
        self.ctx.logger.info(f"create {len(waiting_create_user_dept_relations)} user-department relations")
        # 记录 用户-部门 关系删除日志
        self.ctx.logger.info(f"delete {len(waiting_delete_user_dept_relation_ids)} user-department relations")

    def _get_waiting_create_user_dept_relations(
        self,
        user_dept_id_tuples: Set[Tuple[int, int]],
        exists_user_dept_id_tuples: Set[Tuple[int, int]],
    ) -> List[DataSourceDepartmentUserRelation]:
        # 集合做差，再转换 ID，生成需要创建的 Relations
        waiting_create_user_dept_id_tuples = user_dept_id_tuples - exists_user_dept_id_tuples
        # 如果是不覆盖的场景，则同步前存量的用户，不需要追加关联边
        if not self.overwrite:
            waiting_create_user_dept_id_tuples = {
                (user_id, dept_id)
                for (user_id, dept_id) in waiting_create_user_dept_id_tuples
                if user_id not in self.exists_user_ids_before_sync
            }

        return [
            # NOTE 外键对象也可以直接指定 id 进行初始化
            DataSourceDepartmentUserRelation(user_id=user_id, department_id=dept_id, data_source=self.data_source)
            for (user_id, dept_id) in waiting_create_user_dept_id_tuples
        ]

    def _get_waiting_delete_user_dept_relation_ids(
        self,
        user_code_id_map: Dict[str, int],
        exists_user_dept_relations_map: Dict[Tuple[int, int], int],
        user_dept_id_tuples: Set[Tuple[int, int]],
        exists_user_dept_id_tuples: Set[Tuple[int, int]],
    ) -> List[int]:
        # 集合做差，再转换成 relation ID，得到需要删除的 relation ID 列表
        # 全量模式，没有覆不覆盖一说，就是覆盖，不需要特殊判断
        waiting_delete_user_dept_id_tuples = exists_user_dept_id_tuples - user_dept_id_tuples
        if self.incremental:
            # 增量模式，覆盖，则有新边的用户，老边需要被删除，其他用户关系边不变
            if self.overwrite:
                # 如果指定部门为空，也算是修改了关联边，在覆盖的模式下，需要清理掉旧的数据
                just_update_relation_user_ids = {user_code_id_map[user.code] for user in self.raw_users}
                waiting_delete_user_dept_id_tuples = {
                    (user_id, dept_id)
                    for user_id, dept_id in waiting_delete_user_dept_id_tuples
                    if user_id in just_update_relation_user_ids
                }
            # 增量模式，不覆盖，则直接追加即可，不要删除任何关系边
            else:
                waiting_delete_user_dept_id_tuples = set()

        return [exists_user_dept_relations_map[t] for t in waiting_delete_user_dept_id_tuples]
