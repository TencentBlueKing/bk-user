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

from itertools import groupby
from typing import Dict, List, Set

import pytest
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.sync.contexts import DataSourceSyncTaskContext
from bkuser.apps.sync.syncers import (
    DataSourceDepartmentRelationSyncer,
    DataSourceDepartmentSyncer,
    DataSourceUserDeptRelationSyncer,
    DataSourceUserLeaderRelationSyncer,
    DataSourceUserSyncer,
)
from bkuser.apps.tenant.constants import TenantUserIdRuleEnum
from bkuser.apps.tenant.models import TenantUserIDGenerateConfig
from bkuser.plugins.models import RawDataSourceDepartment, RawDataSourceUser

pytestmark = pytest.mark.django_db


class TestSyncDataSourceUser:
    """数据源用户同步流程测试"""

    def test_initial(
        self, data_source_sync_task_ctx, bare_local_data_source, tenant_user_custom_fields, raw_departments, raw_users
    ):
        # 先同步部门数据，再同步用户数据，做全数据测试
        self._sync_data_source_departments(
            data_source_sync_task_ctx, bare_local_data_source, raw_departments, overwrite=True, incremental=False
        )
        self._sync_data_source_users(
            data_source_sync_task_ctx, bare_local_data_source, raw_users, overwrite=True, incremental=False
        )

        # 验证用户信息
        users = DataSourceUser.objects.filter(data_source=bare_local_data_source)
        assert users.count() == len(raw_users)
        assert set(users.values_list("code", flat=True)) == {user.code for user in raw_users}
        assert set(users.values_list("username", flat=True)) == {user.properties.get("username") for user in raw_users}
        assert set(users.values_list("full_name", flat=True)) == {
            user.properties.get("full_name") for user in raw_users
        }
        assert set(users.values_list("email", flat=True)) == {user.properties.get("email") for user in raw_users}
        assert set(users.values_list("phone", flat=True)) == {user.properties.get("phone") for user in raw_users}
        # 每个的 extras 都是有值的
        assert all(bool(e) for e in users.values_list("extras", flat=True))
        # extras 的 key 应该是和 tenant_user_custom_fields 匹配的
        assert set(users.first().extras.keys()) == {f.name for f in tenant_user_custom_fields}

        # 验证用户部门信息
        assert self._gen_user_depts_from_db(users) == self._gen_user_depts_from_raw_users(raw_users)

        # 验证用户 Leader 信息
        assert self._gen_user_leaders_from_db(users) == self._gen_user_leaders_from_raw_users(raw_users)

    def test_update_with_overwrite(
        self, data_source_sync_task_ctx, full_local_data_source, tenant_user_custom_fields, raw_users, random_raw_user
    ):
        # 1. 修改用户姓名，电话，邮箱，年龄等信息
        raw_users[0].properties["username"] = "zhangsan_rename"
        raw_users[0].properties["full_name"] = "张三的另一个名字"
        raw_users[0].properties["email"] = "zhangsan_rename@m.com"
        raw_users[0].properties["phone"] = "13512345655"
        raw_users[0].properties["phone_country_code"] = "63"
        raw_users[0].properties["age"] = "30"
        # 2. 修改用户 - leader，用户 - 部门关联边
        raw_users[0].leaders = ["linshiyi", "baishier"]
        raw_users[0].departments = ["center_aa", "center_ab"]
        # 3. 修改用户的 code，会导致用户被重建
        lisi_old_code, lisi_new_code = "lisi", "lisi-1"
        raw_users[1].code = lisi_new_code
        # 需要更新其他用户的信息，避免 leader 还是用旧的 Code
        for u in raw_users:
            if lisi_old_code in u.leaders:
                u.leaders.remove(lisi_old_code)
                u.leaders.append(lisi_new_code)
        # 4. 再添加一个随机用户
        raw_users.append(random_raw_user)

        # NOTE: full_local_data_source 中的数据，extras 都是空的，raw_users 中的都非空
        assert not any(
            bool(e)
            for e in DataSourceUser.objects.filter(
                data_source=full_local_data_source,
            ).values_list("extras", flat=True)
        )

        self._sync_data_source_users(
            data_source_sync_task_ctx, full_local_data_source, raw_users, overwrite=True, incremental=False
        )

        users = DataSourceUser.objects.filter(data_source=full_local_data_source)
        assert set(users.values_list("code", flat=True)) == {user.code for user in raw_users}
        assert set(users.values_list("username", flat=True)) == {user.properties.get("username") for user in raw_users}
        # 验证 extras 都被更新
        assert all(bool(e) for e in users.values_list("extras", flat=True))

        # 验证内置/自定义字段被更新
        zhangsan = users.filter(code="zhangsan").first()
        assert zhangsan.username == "zhangsan_rename"
        assert zhangsan.full_name == "张三的另一个名字"
        assert zhangsan.email == "zhangsan_rename@m.com"
        assert zhangsan.phone == "13512345655"
        assert zhangsan.phone_country_code == "63"
        assert zhangsan.extras.get("age") == 30  # noqa: PLR2004

        # 覆盖模式下，会追加关联边
        assert {"linshiyi", "baishier"} == set(
            DataSourceUserLeaderRelation.objects.filter(user=zhangsan).values_list("leader__code", flat=True)
        )
        assert {"center_aa", "center_ab"} == set(
            DataSourceDepartmentUserRelation.objects.filter(user=zhangsan).values_list("department__code", flat=True)
        )

        # 验证用户被重建的情况
        lisi = users.filter(username="lisi").first()
        assert lisi.full_name == "李四"
        assert lisi.email == "lisi@m.com"
        assert lisi.code == "lisi-1"

        # 验证用户部门信息
        assert self._gen_user_depts_from_db(users) == self._gen_user_depts_from_raw_users(raw_users)

        # 验证用户 Leader 信息
        assert self._gen_user_leaders_from_db(users) == self._gen_user_leaders_from_raw_users(raw_users)

    def test_update_without_overwrite(
        self, data_source_sync_task_ctx, full_local_data_source, raw_users, random_raw_user
    ):
        # 修改用户信息
        raw_users[0].properties["username"] = "zhangsan_rename"
        raw_users[0].properties["full_name"] = "张三的另一个名字"
        raw_users[0].properties["email"] = "zhangsan_rename@m.com"
        # 用户 - leader，用户 - 部门关联边
        raw_users[0].leaders = ["linshiyi", "baishier"]
        raw_users[0].departments = ["center_aa", "center_ab"]

        raw_users.append(random_raw_user)

        self._sync_data_source_users(
            data_source_sync_task_ctx, full_local_data_source, raw_users, overwrite=False, incremental=True
        )

        users = DataSourceUser.objects.filter(data_source=full_local_data_source)
        assert set(users.values_list("code", flat=True)) == {user.code for user in raw_users}

        # 没有设置 overview，张三这个 username 不会被更新
        db_usernames = set(users.values_list("username", flat=True))
        raw_usernames = {user.properties.get("username") for user in raw_users}
        assert db_usernames - raw_usernames == {"zhangsan"}
        assert raw_usernames - db_usernames == {"zhangsan_rename"}

        # 验证 extras 都没有被更新 / 新增
        # 注意：即使完全新建的用户也没有，因为没有使用 tenant_user_custom_fields fixture，没有自定义字段
        assert not any(bool(e) for e in users.values_list("extras", flat=True))

        # 验证内置/自定义字段都不会被更新，因为没有选择 overwrite
        zhangsan = users.filter(code="zhangsan").first()
        assert zhangsan.username == "zhangsan"
        assert zhangsan.full_name == "张三"
        assert zhangsan.email == "zhangsan@m.com"
        assert zhangsan.phone == "13512345671"
        assert zhangsan.phone_country_code == "86"
        assert zhangsan.extras == {}

        # 不是覆盖模式，不会追加关联边
        assert DataSourceUserLeaderRelation.objects.filter(user=zhangsan).count() == 0
        assert {"company"} == set(
            DataSourceDepartmentUserRelation.objects.filter(user=zhangsan).values_list("department__code", flat=True)
        )

    def test_update_with_incremental(self, data_source_sync_task_ctx, full_local_data_source, random_raw_user):
        dept_user_relation_cnt_before_sync = DataSourceDepartmentUserRelation.objects.filter(
            data_source=full_local_data_source
        ).count()
        user_leader_relation_cnt_before_sync = DataSourceUserLeaderRelation.objects.filter(
            data_source=full_local_data_source
        ).count()
        user_codes = set(
            DataSourceUser.objects.filter(data_source=full_local_data_source).values_list("code", flat=True)
        )
        user_codes.add(random_raw_user.code)

        self._sync_data_source_users(
            data_source_sync_task_ctx, full_local_data_source, [random_raw_user], overwrite=True, incremental=True
        )

        users = DataSourceUser.objects.filter(data_source=full_local_data_source)
        assert set(users.values_list("code", flat=True)) == user_codes
        # 随机用户属于一个部门 & 拥有一个 leader，因此两种关系的数量应该都是 + 1
        assert DataSourceDepartmentUserRelation.objects.filter(data_source=full_local_data_source).count() == (
            dept_user_relation_cnt_before_sync + 1
        )
        assert DataSourceUserLeaderRelation.objects.filter(data_source=full_local_data_source).count() == (
            user_leader_relation_cnt_before_sync + 1
        )

    def test_update_without_incremental_and_overwrite(
        self, data_source_sync_task_ctx, full_local_data_source, raw_users
    ):
        with pytest.raises(ValueError, match="incremental or overwrite must be True"):
            self._sync_data_source_users(
                data_source_sync_task_ctx, full_local_data_source, raw_users, overwrite=False, incremental=False
            )

    def test_update_with_invalid_leader(self, data_source_sync_task_ctx, full_local_data_source, random_raw_user):
        """全量同步模式，要求用户的 leader 必须也在数据中，否则会有警告"""
        random_raw_user.leaders.append("lisi")

        self._sync_data_source_users(
            data_source_sync_task_ctx, full_local_data_source, [random_raw_user], overwrite=True, incremental=False
        )

        assert data_source_sync_task_ctx.logger.has_warning is True

    def test_update_with_leader_in_db(self, data_source_sync_task_ctx, full_local_data_source, random_raw_user):
        """增量同步模式，用户的 leader 在 db 中存在也是可以的"""
        random_raw_user.leaders.append("lisi")

        self._sync_data_source_users(
            data_source_sync_task_ctx, full_local_data_source, [random_raw_user], overwrite=True, incremental=True
        )

        assert data_source_sync_task_ctx.logger.has_warning is False
        assert DataSourceUser.objects.filter(code=random_raw_user.code).count() == 1

    def test_update_with_invalid_dept(self, data_source_sync_task_ctx, full_local_data_source, random_raw_user):
        """同步要求用户的部门必须已经存在，否则会有警告"""
        random_raw_user.departments.append("not_exists_dept")
        self._sync_data_source_users(
            data_source_sync_task_ctx, full_local_data_source, [random_raw_user], overwrite=True, incremental=False
        )

        assert data_source_sync_task_ctx.logger.has_warning is True

    def test_update_with_unable_update_username(self, data_source_sync_task_ctx, full_local_data_source):
        """对于某些特定的数据源，同步并不会更新 username"""
        raw_users = [
            RawDataSourceUser(
                code="zhangsan",
                properties={
                    "username": "zhangsan_rename",
                    "full_name": "张三重命名",
                    "email": "zhangsan@m.com",
                    "phone": "07712345678",
                    "phone_country_code": "44",
                },
                leaders=[],
                departments=[],
            )
        ]
        # 修改租户用户生成规则表，导致其在同步数据源用户时候无法更新 username
        TenantUserIDGenerateConfig.objects.create(
            data_source=full_local_data_source,
            target_tenant_id=full_local_data_source.owner_tenant_id,
            rule=TenantUserIdRuleEnum.USERNAME_WITH_DOMAIN,
            domain=full_local_data_source.owner_tenant_id,
        )

        self._sync_data_source_users(
            data_source_sync_task_ctx, full_local_data_source, raw_users, overwrite=True, incremental=False
        )

        zhangsan = DataSourceUser.objects.filter(data_source=full_local_data_source, code="zhangsan").first()
        # 不支持数据源用户的 username 更新的情况
        assert zhangsan.username == "zhangsan"
        assert zhangsan.full_name == "张三重命名"
        assert zhangsan.email == "zhangsan@m.com"

    def test_destroy(self, data_source_sync_task_ctx, full_local_data_source):
        raw_users: List[RawDataSourceUser] = []

        self._sync_data_source_users(
            data_source_sync_task_ctx, full_local_data_source, raw_users, overwrite=True, incremental=False
        )
        assert DataSourceUser.objects.filter(data_source=full_local_data_source).count() == 0

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
    def _sync_data_source_users(
        data_source_sync_task_ctx: DataSourceSyncTaskContext,
        data_source: DataSource,
        raw_users: List[RawDataSourceUser],
        overwrite: bool,
        incremental: bool,
    ):
        """执行数据源部门同步（所有步骤）"""
        kwargs = {
            "ctx": data_source_sync_task_ctx,
            "data_source": data_source,
            "raw_users": raw_users,
            "overwrite": overwrite,
            "incremental": incremental,
        }
        DataSourceUserSyncer(**kwargs).sync()  # type: ignore
        DataSourceUserLeaderRelationSyncer(**kwargs).sync()  # type: ignore
        DataSourceUserDeptRelationSyncer(**kwargs).sync()  # type: ignore

    @staticmethod
    def _gen_user_leaders_from_raw_users(raw_users: List[RawDataSourceUser]) -> Dict[str, Set[str]]:
        return {u.code: set(u.leaders) for u in raw_users if u.leaders}

    @staticmethod
    def _gen_user_leaders_from_db(data_source_users: List[DataSourceUser]) -> Dict[str, Set[str]]:
        relations = (
            DataSourceUserLeaderRelation.objects.filter(user__in=data_source_users)
            .order_by("user_id")
            .values("user__code", "leader__code")
        )
        return {
            user_code: {r["leader__code"] for r in group}
            for user_code, group in groupby(relations, key=lambda r: r["user__code"])
        }

    @staticmethod
    def _gen_user_depts_from_raw_users(raw_users: List[RawDataSourceUser]) -> Dict[str, Set[str]]:
        return {u.code: set(u.departments) for u in raw_users if u.departments}

    @staticmethod
    def _gen_user_depts_from_db(data_source_users: List[DataSourceUser]) -> Dict[str, Set[str]]:
        relations = (
            DataSourceDepartmentUserRelation.objects.filter(user__in=data_source_users)
            .order_by("user_id")
            .values("user__code", "department__code")
        )
        return {
            user_code: {r["department__code"] for r in group}
            for user_code, group in groupby(relations, key=lambda r: r["user__code"])
        }
