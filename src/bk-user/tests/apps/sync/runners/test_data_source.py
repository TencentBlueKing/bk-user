# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

from typing import List, Tuple

import pytest
from bkuser.apps.data_source.constants import DataSourceUsernameGenerateRule
from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
    DataSourceUsernameGenerateConfig,
)
from bkuser.apps.sync.constants import SyncTaskStatus
from bkuser.apps.sync.runners import DataSourceSyncTaskRunner
from bkuser.plugins.local.utils import gen_dept_code
from openpyxl.workbook import Workbook

pytestmark = pytest.mark.django_db


@pytest.fixture
def _init_data_source_users_depts(bare_local_data_source):
    """初始化存量部门 & 用户数据"""
    ds = bare_local_data_source

    # 部门
    company = DataSourceDepartment.objects.create(data_source=ds, code=gen_dept_code("公司"), name="公司")
    dept_a = DataSourceDepartment.objects.create(data_source=ds, code=gen_dept_code("公司/部门A"), name="部门A")
    dept_x = DataSourceDepartment.objects.create(data_source=ds, code=gen_dept_code("公司/部门X"), name="部门X")
    # 部门关系
    company_node = DataSourceDepartmentRelation.objects.create(department=company, parent=None, data_source=ds)
    DataSourceDepartmentRelation.objects.create(data_source=ds, parent=company_node, department=dept_a)
    DataSourceDepartmentRelation.objects.create(data_source=ds, parent=company_node, department=dept_x)

    # 用户
    zhangsan = DataSourceUser.objects.create(data_source=ds, code="zhangsan", username="zhangsan", full_name="张三")
    lisi = DataSourceUser.objects.create(data_source=ds, code="lisi", username="lisi", full_name="李四")
    user_x = DataSourceUser.objects.create(data_source=ds, code="user_x", username="user_x", full_name="用户X")
    # 用户 leader 关系
    DataSourceUserLeaderRelation.objects.create(data_source=ds, user=lisi, leader=zhangsan)
    DataSourceUserLeaderRelation.objects.create(data_source=ds, user=user_x, leader=lisi)
    # 用户部门关系
    DataSourceDepartmentUserRelation.objects.create(data_source=ds, user=zhangsan, department=company)
    DataSourceDepartmentUserRelation.objects.create(data_source=ds, user=user_x, department=dept_x)


class TestDataSourceSyncRunner:
    """测试数据源同步"""

    @pytest.mark.parametrize(
        ("incremental", "overwrite"),
        [
            # 数据源同步模式：全量 & 覆盖
            (False, True),
            # 本地数据源导入模式：增量 & 不覆盖
            (True, False),
            # 未使用模式：增量 & 覆盖
            (True, True),
        ],
    )
    def test_initial(self, bare_local_data_source, data_source_sync_task, user_workbook, incremental, overwrite):
        data_source_sync_task.extras = {"overwrite": overwrite, "incremental": incremental}
        data_source_sync_task.save()

        DataSourceSyncTaskRunner(data_source_sync_task, {"workbook": user_workbook}).run()

        data_source_sync_task.refresh_from_db()
        assert data_source_sync_task.status == SyncTaskStatus.SUCCESS

        # 部门
        assert DataSourceDepartment.objects.filter(data_source=bare_local_data_source).count() == 12
        assert DataSourceDepartmentRelation.objects.filter(data_source=bare_local_data_source).count() == 12

        # 用户
        assert DataSourceUser.objects.filter(data_source=bare_local_data_source).count() == 12
        assert DataSourceUserLeaderRelation.objects.filter(data_source=bare_local_data_source).count() == 12
        assert DataSourceDepartmentUserRelation.objects.filter(data_source=bare_local_data_source).count() == 14

    @pytest.mark.parametrize(
        (
            "incremental",
            "overwrite",
            "dept_cnt",
            "dept_rel_cnt",
            "user_cnt",
            "user_leader_rel_cnt",
            "user_dept_rel_cnt",
        ),
        [
            # 数据源同步模式：全量 & 覆盖
            (False, True, 12, 12, 12, 12, 14),
            # 本地数据源导入模式：增量 & 不覆盖
            # lisi 是存量用户，不会修改 leader & dept 关联边
            (True, False, 13, 13, 13, 13, 13),
            # 未使用模式：增量 & 覆盖
            (True, True, 13, 13, 13, 13, 15),
        ],
    )
    @pytest.mark.usefixtures("_init_data_source_users_depts")
    def test_update(
        self,
        bare_local_data_source,
        data_source_sync_task,
        user_workbook,
        incremental,
        overwrite,
        dept_cnt,
        dept_rel_cnt,
        user_cnt,
        user_leader_rel_cnt,
        user_dept_rel_cnt,
    ):
        data_source_sync_task.extras = {"overwrite": overwrite, "incremental": incremental}
        data_source_sync_task.save()

        DataSourceSyncTaskRunner(data_source_sync_task, {"workbook": user_workbook}).run()

        data_source_sync_task.refresh_from_db()
        assert data_source_sync_task.status == SyncTaskStatus.SUCCESS

        # 部门
        assert DataSourceDepartment.objects.filter(data_source=bare_local_data_source).count() == dept_cnt
        assert DataSourceDepartmentRelation.objects.filter(data_source=bare_local_data_source).count() == dept_rel_cnt

        # 用户
        assert DataSourceUser.objects.filter(data_source=bare_local_data_source).count() == user_cnt
        assert (
            DataSourceUserLeaderRelation.objects.filter(data_source=bare_local_data_source).count()
            == user_leader_rel_cnt
        )
        assert (
            DataSourceDepartmentUserRelation.objects.filter(data_source=bare_local_data_source).count()
            == user_dept_rel_cnt
        )


def _gen_user_row(username: str, phone: str, leaders: str | None = None) -> Tuple:
    """生成导入文件中的用户数据行（用户名 / 姓名 / 邮箱 / 手机号 / 组织 / 直接上级 / 年龄 / 性别 / 籍贯）"""
    return (username, username, f"{username}@m.com", phone, None, leaders, "20", "male", "region-0")


def _gen_workbook(user_workbook: Workbook, rows: List[Tuple]) -> Workbook:
    """保留填写须知与表头，替换为指定的用户数据"""
    sheet = user_workbook["users"]
    sheet.delete_rows(3, sheet.max_row)
    for row in rows:
        sheet.append(row)
    return user_workbook


def _create_data_source_user(data_source, username: str, phone: str) -> DataSourceUser:
    return DataSourceUser.objects.create(
        data_source=data_source,
        code=username,
        username=username,
        full_name=username,
        email=f"{username}@m.com",
        phone=phone,
    )


class TestDataSourceSyncRunnerExcludeConflictUsers:
    """测试数据源同步时排除与同租户其他数据源用户名冲突的用户"""

    @staticmethod
    def _run(task, workbook: Workbook, incremental: bool, overwrite: bool):
        task.extras = {"overwrite": overwrite, "incremental": incremental}
        task.save()

        DataSourceSyncTaskRunner(task, {"workbook": workbook}).run()

        task.refresh_from_db()

    @pytest.mark.parametrize(
        ("incremental", "overwrite"),
        [
            # 数据源同步模式：全量 & 覆盖
            (False, True),
            # 本地数据源导入模式：增量 & 不覆盖
            (True, False),
            # 本地数据源导入模式：增量 & 覆盖
            (True, True),
        ],
    )
    def test_exclude_conflict_users(
        self,
        bare_local_data_source,
        bare_local_data_source_b,
        data_source_sync_task,
        user_workbook,
        incremental,
        overwrite,
    ):
        _create_data_source_user(bare_local_data_source_b, "zhangsan", "13500000001")
        rows = [
            _gen_user_row("zhangsan", "13500000002"),
            # Leader 为被排除的冲突用户，不应导致关系同步报错
            _gen_user_row("lisi", "13500000003", leaders="zhangsan"),
        ]

        self._run(
            data_source_sync_task, _gen_workbook(user_workbook, rows), incremental=incremental, overwrite=overwrite
        )

        assert data_source_sync_task.status == SyncTaskStatus.SUCCESS
        assert data_source_sync_task.has_warning
        assert "zhangsan" in data_source_sync_task.logs
        assert "1 users remain after excluding username conflict users" in data_source_sync_task.logs

        users = DataSourceUser.objects.filter(data_source=bare_local_data_source)
        assert list(users.values_list("username", flat=True)) == ["lisi"]
        assert not DataSourceUserLeaderRelation.objects.filter(data_source=bare_local_data_source).exists()

    def test_exclude_conflict_users_case_insensitive(
        self, bare_local_data_source, bare_local_data_source_b, data_source_sync_task, user_workbook
    ):
        _create_data_source_user(bare_local_data_source_b, "zhangsan", "13500000001")
        rows = [_gen_user_row("ZhangSan", "13500000002"), _gen_user_row("lisi", "13500000003")]

        self._run(data_source_sync_task, _gen_workbook(user_workbook, rows), incremental=True, overwrite=True)

        assert data_source_sync_task.status == SyncTaskStatus.SUCCESS
        assert "ZhangSan" in data_source_sync_task.logs

        users = DataSourceUser.objects.filter(data_source=bare_local_data_source)
        assert list(users.values_list("username", flat=True)) == ["lisi"]

    def test_exclude_conflict_users_with_username_affix(
        self, bare_local_data_source, bare_local_data_source_b, data_source_sync_task, user_workbook
    ):
        DataSourceUsernameGenerateConfig.objects.create(
            data_source=bare_local_data_source,
            rule=DataSourceUsernameGenerateRule.ADD_AFFIX,
            prefix="ds1_",
            suffix="",
        )
        _create_data_source_user(bare_local_data_source_b, "ds1_zhangsan", "13500000001")
        rows = [_gen_user_row("zhangsan", "13500000002"), _gen_user_row("lisi", "13500000003")]

        self._run(data_source_sync_task, _gen_workbook(user_workbook, rows), incremental=True, overwrite=True)

        assert data_source_sync_task.status == SyncTaskStatus.SUCCESS
        assert "ds1_zhangsan" in data_source_sync_task.logs

        users = DataSourceUser.objects.filter(data_source=bare_local_data_source)
        assert list(users.values_list("username", flat=True)) == ["ds1_lisi"]

    def test_keep_exists_conflict_user_relations(
        self, bare_local_data_source, bare_local_data_source_b, data_source_sync_task, user_workbook
    ):
        """本数据源已存在的冲突用户被排除后，其 Leader 关系不应被修改"""
        zhangsan = _create_data_source_user(bare_local_data_source, "zhangsan", "13500000001")
        lisi = _create_data_source_user(bare_local_data_source, "lisi", "13500000002")
        _create_data_source_user(bare_local_data_source, "wangwu", "13500000003")
        DataSourceUserLeaderRelation.objects.create(data_source=bare_local_data_source, user=zhangsan, leader=lisi)

        _create_data_source_user(bare_local_data_source_b, "zhangsan", "13500000004")
        rows = [_gen_user_row("zhangsan", "13500000001", leaders="wangwu")]

        self._run(data_source_sync_task, _gen_workbook(user_workbook, rows), incremental=True, overwrite=True)

        assert data_source_sync_task.status == SyncTaskStatus.SUCCESS
        relations = DataSourceUserLeaderRelation.objects.filter(data_source=bare_local_data_source)
        assert set(relations.values_list("user__code", "leader__code")) == {("zhangsan", "lisi")}

    def test_same_data_source_user_not_conflict(self, bare_local_data_source, data_source_sync_task, user_workbook):
        """同数据源已有的同名用户不算冲突，应正常更新"""
        _create_data_source_user(bare_local_data_source, "zhangsan", "13500000001")
        rows = [_gen_user_row("zhangsan", "13500000009")]

        self._run(data_source_sync_task, _gen_workbook(user_workbook, rows), incremental=True, overwrite=True)

        assert data_source_sync_task.status == SyncTaskStatus.SUCCESS
        assert not data_source_sync_task.has_warning
        assert DataSourceUser.objects.get(data_source=bare_local_data_source, code="zhangsan").phone == "13500000009"
