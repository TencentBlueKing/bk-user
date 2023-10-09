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
from typing import List

import pytest
from bkuser.apps.sync.constants import SyncTaskStatus, SyncTaskTrigger
from bkuser.apps.sync.models import DataSourceSyncTask, TenantSyncTask
from bkuser.plugins.models import Department, Leader, RawDataSourceDepartment, RawDataSourceUser
from django.utils import timezone

from tests.test_utils.helpers import generate_random_string


@pytest.fixture()
def data_source_sync_task(bare_local_data_source) -> DataSourceSyncTask:
    """数据源同步任务"""
    return DataSourceSyncTask.objects.create(
        data_source_id=bare_local_data_source.id,
        status=SyncTaskStatus.PENDING,
        trigger=SyncTaskTrigger.MANUAL,
        operator="admin",
        start_at=timezone.now(),
        extra={"overwrite": True, "async_run": False},
    )


@pytest.fixture()
def tenant_sync_task(bare_local_data_source, default_tenant) -> TenantSyncTask:
    """租户数据同步任务"""
    return TenantSyncTask(
        tenant_id=default_tenant.id,
        data_source_id=bare_local_data_source.id,
        status=SyncTaskStatus.PENDING,
        trigger=SyncTaskTrigger.MANUAL,
        operator="admin",
        start_at=timezone.now(),
        extra={"async_run": False},
    )


@pytest.fixture()
def raw_departments() -> List[RawDataSourceDepartment]:
    """数据源插件提供的原始部门信息"""
    return [
        RawDataSourceDepartment(code="company", name="公司", parent=None),
        RawDataSourceDepartment(code="dept_a", name="部门A", parent="company"),
        RawDataSourceDepartment(code="dept_b", name="部门B", parent="company"),
        RawDataSourceDepartment(code="center_aa", name="中心AA", parent="dept_a"),
        RawDataSourceDepartment(code="center_ab", name="中心AB", parent="dept_a"),
        RawDataSourceDepartment(code="center_ba", name="中心BA", parent="dept_b"),
        RawDataSourceDepartment(code="group_aaa", name="小组AAA", parent="center_aa"),
        RawDataSourceDepartment(code="group_aba", name="小组ABA", parent="center_ab"),
        RawDataSourceDepartment(code="group_baa", name="小组BAA", parent="center_ba"),
        RawDataSourceDepartment(code="v", name="V", parent=None),
    ]


@pytest.fixture()
def raw_users() -> List[RawDataSourceUser]:
    """数据源插件提供的原始用户信息"""
    return [
        RawDataSourceUser(
            code="Employee-3",
            properties={
                "username": "zhangsan",
                "full_name": "张三",
                "email": "zhangsan@m.com",
                "phone": "13512345671",
                "age": "18",
                "gender": "male",
                "region": "beijing",
            },
            leaders=[],
            departments=[Department("company", "公司")],
        ),
        RawDataSourceUser(
            code="Employee-4",
            properties={
                "username": "lisi",
                "full_name": "李四",
                "email": "lisi@m.com",
                "phone": "13512345672",
                "age": "28",
                "gender": "female",
                "region": "shanghai",
            },
            leaders=[
                Leader("Employee-3", "zhangsan"),
            ],
            departments=[
                Department("dept_a", "公司/部门A"),
                Department("center_aa", "公司/部门A/中心AA"),
            ],
        ),
        RawDataSourceUser(
            code="Employee-5",
            properties={
                "username": "wangwu",
                "full_name": "王五",
                "email": "wangwu@m.com",
                "phone": "13512345673",
                "age": "38",
                "gender": "male",
                "region": "shenzhen",
            },
            leaders=[
                Leader("Employee-3", "zhangsan"),
            ],
            departments=[
                Department("dept_a", "公司/部门A"),
                Department("dept_b", "公司/部门B"),
            ],
        ),
        RawDataSourceUser(
            code="Employee-6",
            properties={
                "username": "zhaoliu",
                "full_name": "赵六",
                "email": "zhaoliu@m.com",
                "phone": "13512345674",
                "age": "33",
                "gender": "female",
                "region": "tianjin",
            },
            leaders=[
                Leader("Employee-4", "lisi"),
            ],
            departments=[
                Department("center_aa", "公司/部门A/中心AA"),
            ],
        ),
        RawDataSourceUser(
            code="Employee-7",
            properties={
                "username": "liuqi",
                "full_name": "柳七",
                "email": "liuqi@m.com",
                "phone": "13512345675",
                "age": "25",
                "gender": "female",
                "region": "jiangxi",
            },
            leaders=[
                Leader("Employee-6", "zhaoliu"),
            ],
            departments=[
                Department("group_aaa", "公司/部门A/中心AA/小组AAA"),
            ],
        ),
        RawDataSourceUser(
            code="Employee-8",
            properties={
                "username": "maiba",
                "full_name": "麦八",
                "email": "maiba@m.com",
                "phone": "13512345676",
                "age": "35",
                "gender": "male",
                "region": "xinjiang",
            },
            leaders=[
                Leader("Employee-4", "lisi"),
                Leader("Employee-5", "wangwu"),
            ],
            departments=[
                Department("center_ab", "公司/部门A/中心AB"),
            ],
        ),
        RawDataSourceUser(
            code="Employee-9",
            properties={
                "username": "yangjiu",
                "full_name": "杨九",
                "email": "yangjiu@m.com",
                "phone": "13512345677",
                "age": "40",
                "gender": "male",
                "region": "guangdong",
            },
            leaders=[
                Leader("Employee-5", "wangwu"),
            ],
            departments=[
                Department("center_ab", "公司/部门A/中心AB"),
            ],
        ),
        RawDataSourceUser(
            code="Employee-10",
            properties={
                "username": "lushi",
                "full_name": "鲁十",
                "email": "lushi@m.com",
                "phone": "13512345678",
                "age": "50",
                "gender": "male",
                "region": "jiangsu",
            },
            leaders=[
                Leader("Employee-5", "wangwu"),
                Leader("Employee-8", "maiba"),
            ],
            departments=[
                Department("group_aba", "公司/部门A/中心AB/小组ABA"),
                Department("center_ba", "公司/部门A/中心BA"),
            ],
        ),
        RawDataSourceUser(
            code="Employee-11",
            properties={
                "username": "linshiyi",
                "full_name": "林十一",
                "email": "linshiyi@m.com",
                "phone": "13512345679",
                "age": "31",
                "gender": "male",
                "region": "hunan",
            },
            leaders=[
                Leader("Employee-10", "lushi"),
            ],
            departments=[
                Department("group_aba", "公司/部门A/中心AB/小组ABA"),
            ],
        ),
        RawDataSourceUser(
            code="Employee-12",
            properties={
                "username": "baishier",
                "full_name": "白十二",
                "email": "baishier@m.com",
                "phone": "13512345670",
                "age": "30",
                "gender": "female",
                "region": "guangdong",
            },
            leaders=[
                Leader("Employee-10", "lushi"),
            ],
            departments=[
                Department("group_baa", "公司/部门B/中心BA/小组BAA"),
            ],
        ),
        RawDataSourceUser(
            code="Employee-666",
            properties={
                "username": "freedom",
                "full_name": "自由人",
                "email": "freedom@m.com",
                "phone": "1351234567X",
                "age": "999",
                "gender": "other",
                "region": "solar system",
            },
            leaders=[],
            departments=[],
        ),
    ]


@pytest.fixture()
def random_raw_user() -> RawDataSourceUser:
    """生成随机用户"""
    return RawDataSourceUser(
        code=generate_random_string(),
        properties={
            "username": "user_random",
            "full_name": "随机用户",
            "email": "random@m.com",
            "phone": "13512345670",
            "phone_country_code": "85",
            "age": "66",
            "gender": "other",
            "region": "shangxi",
        },
        leaders=[],
        departments=[],
    )
