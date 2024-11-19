# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
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
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

import pytest
from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.sync.constants import SyncTaskStatus
from bkuser.apps.sync.runners import DataSourceSyncTaskRunner
from bkuser.plugins.local.utils import gen_dept_code

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
