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
from itertools import groupby
from typing import Dict, List, Set, Tuple

import pytest
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.sync.syncers import (
    DataSourceDepartmentSyncer,
    DataSourceUserSyncer,
    TenantDepartmentSyncer,
    TenantUserSyncer,
)
from bkuser.apps.tenant.models import Tenant, TenantDepartment, TenantUser
from bkuser.common.constants import PERMANENT_TIME
from bkuser.plugins.models import RawDataSourceDepartment, RawDataSourceUser
from bkuser.utils.uuid import generate_uuid

pytestmark = pytest.mark.django_db


class TestDataSourceDepartmentSyncer:
    def test_initial(self, data_source_sync_task_ctx, bare_local_data_source, raw_departments):
        DataSourceDepartmentSyncer(data_source_sync_task_ctx, bare_local_data_source, raw_departments).sync()

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
            RawDataSourceDepartment(code="company", name="公司", parent=None),
            RawDataSourceDepartment(code="dept_a", name="部门A(重命名)", parent="company"),
            RawDataSourceDepartment(code="dept_c", name="部门C", parent="company"),
            RawDataSourceDepartment(code="center_ca", name="中心CA", parent="dept_c"),
        ]
        DataSourceDepartmentSyncer(data_source_sync_task_ctx, full_local_data_source, raw_departments).sync()

        # 验证部门信息
        departments = DataSourceDepartment.objects.filter(data_source=full_local_data_source)
        assert departments.count() == len(raw_departments)
        assert set(departments.values_list("code", flat=True)) == {dept.code for dept in raw_departments}
        assert set(departments.values_list("name", flat=True)) == {dept.name for dept in raw_departments}

        # 验证部门关系信息
        assert self._gen_parent_relations_from_db(
            data_source=full_local_data_source
        ) == self._gen_parent_relations_from_raw_departments(raw_departments)

    def test_destroy(self, data_source_sync_task_ctx, full_local_data_source):
        raw_departments: List[RawDataSourceDepartment] = []
        DataSourceDepartmentSyncer(data_source_sync_task_ctx, full_local_data_source, raw_departments).sync()

        # 同步了空的数据，导致该数据源的所有部门，部门关系信息都被删除
        assert not DataSourceDepartment.objects.filter(data_source=full_local_data_source).exists()
        assert not DataSourceDepartmentRelation.objects.filter(data_source=full_local_data_source).exists()

    @staticmethod
    def _gen_parent_relations_from_raw_departments(
        raw_depts: List[RawDataSourceDepartment],
    ) -> Set[Tuple[str, str | None]]:
        return {(dept.code, dept.parent) for dept in raw_depts}

    @staticmethod
    def _gen_parent_relations_from_db(data_source: DataSource) -> Set[Tuple[str, str | None]]:
        dept_relations = DataSourceDepartmentRelation.objects.filter(data_source=data_source)
        return {(rel.department.code, rel.parent.department.code if rel.parent else None) for rel in dept_relations}


class TestDataSourceUserSyncer:
    def test_initial(
        self,
        data_source_sync_task_ctx,
        bare_local_data_source,
        tenant_user_custom_fields,
        raw_departments,
        raw_users,
    ):
        # 先同步部门数据，再同步用户数据
        DataSourceDepartmentSyncer(data_source_sync_task_ctx, bare_local_data_source, raw_departments).sync()
        DataSourceUserSyncer(
            data_source_sync_task_ctx,
            bare_local_data_source,
            raw_users,
            overwrite=True,
            incremental=False,
        ).sync()

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
        self,
        data_source_sync_task_ctx,
        full_local_data_source,
        tenant_user_custom_fields,
        raw_users,
        random_raw_user,
    ):
        # 1. 修改用户姓名，电话，邮箱，年龄等信息
        # su 注：用户名更新暂时被禁用，需要进一步讨论策略
        # raw_users[0].properties["username"] = "zhangsan_rename"
        raw_users[0].properties["full_name"] = "张三的另一个名字"
        raw_users[0].properties["email"] = "zhangsan_rename@m.com"
        raw_users[0].properties["phone"] = "13512345655"
        raw_users[0].properties["phone_country_code"] = "63"
        raw_users[0].properties["age"] = "30"
        # 2. 修改用户的 code，会导致用户被重建
        lisi_old_code, lisi_new_code = "lisi", "lisi-1"
        raw_users[1].code = lisi_new_code
        # 需要更新其他用户的信息，避免 leader 还是用旧的 Code
        for u in raw_users:
            if lisi_old_code in u.leaders:
                u.leaders.remove(lisi_old_code)
                u.leaders.append(lisi_new_code)
        # 3. 再添加一个随机用户
        raw_users.append(random_raw_user)

        # NOTE: full_local_data_source 中的数据，extras 都是空的，raw_users 中的都非空
        assert not any(
            bool(e)
            for e in DataSourceUser.objects.filter(
                data_source=full_local_data_source,
            ).values_list("extras", flat=True)
        )

        DataSourceUserSyncer(
            data_source_sync_task_ctx,
            full_local_data_source,
            raw_users,
            overwrite=True,
            incremental=False,
        ).sync()

        users = DataSourceUser.objects.filter(data_source=full_local_data_source)
        assert set(users.values_list("code", flat=True)) == {user.code for user in raw_users}
        assert set(users.values_list("username", flat=True)) == {user.properties.get("username") for user in raw_users}
        # 验证 extras 都被更新
        assert all(bool(e) for e in users.values_list("extras", flat=True))

        # 验证内置/自定义字段被更新
        zhangsan = users.filter(code="zhangsan").first()
        # su 注：用户名更新暂时被禁用，需要进一步讨论策略
        # assert zhangsan.username == "zhangsan_rename"
        assert zhangsan.full_name == "张三的另一个名字"
        assert zhangsan.email == "zhangsan_rename@m.com"
        assert zhangsan.phone == "13512345655"
        assert zhangsan.phone_country_code == "63"
        assert zhangsan.extras.get("age") == "30"

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

        raw_users.append(random_raw_user)

        DataSourceUserSyncer(
            data_source_sync_task_ctx,
            full_local_data_source,
            raw_users,
            overwrite=False,
            incremental=False,
        ).sync()

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

    def test_update_with_incremental(self, data_source_sync_task_ctx, full_local_data_source, random_raw_user):
        user_codes = set(
            DataSourceUser.objects.filter(
                data_source=full_local_data_source,
            ).values_list("code", flat=True)
        )
        user_codes.add(random_raw_user.code)
        DataSourceUserSyncer(
            data_source_sync_task_ctx,
            full_local_data_source,
            [random_raw_user],
            overwrite=True,
            incremental=True,
        ).sync()

        users = DataSourceUser.objects.filter(data_source=full_local_data_source)
        assert set(users.values_list("code", flat=True)) == user_codes

    def test_update_with_invalid_leader(self, data_source_sync_task_ctx, full_local_data_source, random_raw_user):
        """全量同步模式，要求用户的 leader 必须也在数据中，否则会有警告"""
        random_raw_user.leaders.append("lisi")
        DataSourceUserSyncer(
            data_source_sync_task_ctx,
            full_local_data_source,
            [random_raw_user],
            overwrite=True,
            incremental=False,
        ).sync()

        assert data_source_sync_task_ctx.logger.has_warning is True

    def test_update_with_leader_in_db(self, data_source_sync_task_ctx, full_local_data_source, random_raw_user):
        """增量同步模式，用户的 leader 在 db 中存在也是可以的"""
        random_raw_user.leaders.append("lisi")

        DataSourceUserSyncer(
            data_source_sync_task_ctx,
            full_local_data_source,
            [random_raw_user],
            overwrite=True,
            incremental=True,
        ).sync()

        assert data_source_sync_task_ctx.logger.has_warning is False
        assert DataSourceUser.objects.filter(code=random_raw_user.code).count() == 1

    def test_update_with_invalid_dept(self, data_source_sync_task_ctx, full_local_data_source, random_raw_user):
        """同步要求用户的部门必须已经存在，否则会有警告"""
        random_raw_user.departments.append("not_exists_dept")
        DataSourceUserSyncer(
            data_source_sync_task_ctx,
            full_local_data_source,
            [random_raw_user],
            overwrite=True,
            incremental=False,
        ).sync()

        assert data_source_sync_task_ctx.logger.has_warning is True

    def test_destroy(self, data_source_sync_task_ctx, full_local_data_source):
        raw_users: List[RawDataSourceUser] = []

        DataSourceUserSyncer(
            data_source_sync_task_ctx,
            full_local_data_source,
            raw_users,
            overwrite=True,
            incremental=False,
        ).sync()
        assert DataSourceUser.objects.filter(data_source=full_local_data_source).count() == 0

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


class TestTenantDepartmentSyncer:
    def test_cud(self, tenant_sync_task_ctx, full_local_data_source, bare_general_data_source, default_tenant):
        # 另外的数据源同步到租户的数据
        other_ds_dept = DataSourceDepartment.objects.create(
            data_source=bare_general_data_source, code="company_x", name="公司X"
        )
        TenantDepartment.objects.create(
            tenant=default_tenant,
            data_source=bare_general_data_source,
            data_source_department=other_ds_dept,
        )

        # 初始化场景
        TenantDepartmentSyncer(tenant_sync_task_ctx, full_local_data_source, default_tenant).sync()
        assert self._gen_ds_dept_ids_with_data_source(
            data_source=full_local_data_source
        ) == self._gen_ds_dept_ids_with_tenant(default_tenant, full_local_data_source)

        # 更新场景
        DataSourceDepartment.objects.filter(
            data_source=full_local_data_source, code__in=["center_ba", "group_baa"]
        ).delete()
        DataSourceDepartment.objects.create(data_source=full_local_data_source, code="center_ac", name="中心AC")

        TenantDepartmentSyncer(tenant_sync_task_ctx, full_local_data_source, default_tenant).sync()
        assert self._gen_ds_dept_ids_with_data_source(
            data_source=full_local_data_source
        ) == self._gen_ds_dept_ids_with_tenant(default_tenant, full_local_data_source)

        # 删除场景，只会删除当前数据源关联的租户部门
        DataSourceDepartment.objects.filter(data_source=full_local_data_source).delete()
        TenantDepartmentSyncer(tenant_sync_task_ctx, full_local_data_source, default_tenant).sync()

        tenant_depts = TenantDepartment.objects.filter(tenant=default_tenant)
        assert tenant_depts.exists()
        assert not tenant_depts.filter(data_source=full_local_data_source).exists()

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


class TestTenantUserSyncer:
    def test_cud(
        self,
        tenant_sync_task_ctx,
        full_local_data_source,
        bare_general_data_source,
        default_tenant,
    ):
        # 另外的数据源同步到租户的数据
        other_ds_user = DataSourceUser.objects.create(
            data_source=bare_general_data_source,
            code="libai",
            username="libai",
            full_name="李白",
            email="libai@m.com",
            phone="13512345991",
        )
        TenantUser.objects.create(
            id=generate_uuid(),
            tenant=default_tenant,
            data_source_user=other_ds_user,
            data_source=bare_general_data_source,
            account_expired_at=PERMANENT_TIME,
        )

        # 初始化场景
        TenantUserSyncer(tenant_sync_task_ctx, full_local_data_source, default_tenant).sync()
        assert self._gen_ds_user_ids_with_data_source(
            data_source=full_local_data_source
        ) == self._gen_ds_user_ids_with_tenant(default_tenant, full_local_data_source)

        # 更新场景
        DataSourceUser.objects.filter(
            data_source=full_local_data_source,
            code__in=["yangjiu", "lushi"],
        ).delete()
        DataSourceUser.objects.create(
            data_source=full_local_data_source,
            code="xiaoershi",
            username="xiaoershi",
            full_name="萧二十",
            email="xiaoershi@m.com",
            phone="13512345999",
        )

        TenantUserSyncer(tenant_sync_task_ctx, full_local_data_source, default_tenant).sync()
        assert self._gen_ds_user_ids_with_data_source(
            data_source=full_local_data_source
        ) == self._gen_ds_user_ids_with_tenant(default_tenant, full_local_data_source)

        # 删除场景，只会删除当前数据源关联的租户用户
        DataSourceUser.objects.filter(data_source=full_local_data_source).delete()
        TenantUserSyncer(tenant_sync_task_ctx, full_local_data_source, default_tenant).sync()

        tenant_users = TenantUser.objects.filter(tenant=default_tenant)
        assert tenant_users.exists()
        assert not tenant_users.filter(data_source=full_local_data_source).exists()

    @staticmethod
    def _gen_ds_user_ids_with_tenant(tenant: Tenant, data_source: DataSource) -> Set[int]:
        return set(
            TenantUser.objects.filter(
                tenant=tenant,
                data_source=data_source,
            ).values_list("data_source_user_id", flat=True)
        )

    @staticmethod
    def _gen_ds_user_ids_with_data_source(data_source: DataSource) -> Set[int]:
        return set(DataSourceUser.objects.filter(data_source=data_source).values_list("id", flat=True))
