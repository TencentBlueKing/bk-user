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
from bkuser.apps.sync.context import DataSourceSyncTaskContext, TenantSyncTaskContext
from bkuser.apps.sync.models import DataSourceSyncTask, TenantSyncTask
from bkuser.plugins.models import RawDataSourceDepartment, RawDataSourceUser
from django.utils import timezone

from tests.test_utils.helpers import generate_random_string


@pytest.fixture()
def data_source_sync_task(bare_local_data_source) -> DataSourceSyncTask:
    """数据源同步任务"""
    return DataSourceSyncTask.objects.create(
        data_source=bare_local_data_source,
        status=SyncTaskStatus.PENDING,
        trigger=SyncTaskTrigger.MANUAL,
        operator="admin",
        start_at=timezone.now(),
        extras={"overwrite": True, "async_run": False},
    )


@pytest.fixture()
def data_source_sync_task_ctx(data_source_sync_task) -> DataSourceSyncTaskContext:
    return DataSourceSyncTaskContext(data_source_sync_task)


@pytest.fixture()
def tenant_sync_task(bare_local_data_source, default_tenant) -> TenantSyncTask:
    """租户数据同步任务"""
    return TenantSyncTask.objects.create(
        tenant=default_tenant,
        data_source=bare_local_data_source,
        status=SyncTaskStatus.PENDING,
        trigger=SyncTaskTrigger.MANUAL,
        operator="admin",
        start_at=timezone.now(),
        extras={"async_run": False},
    )


@pytest.fixture()
def tenant_sync_task_ctx(tenant_sync_task) -> TenantSyncTaskContext:
    return TenantSyncTaskContext(tenant_sync_task)


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
            code="zhangsan",
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
            departments=["company"],
        ),
        RawDataSourceUser(
            code="lisi",
            properties={
                "username": "lisi",
                "full_name": "李四",
                "email": "lisi@m.com",
                "phone": "13512345672",
                "age": "28",
                "gender": "female",
                "region": "shanghai",
            },
            leaders=["zhangsan"],
            departments=["dept_a", "center_aa"],
        ),
        RawDataSourceUser(
            code="wangwu",
            properties={
                "username": "wangwu",
                "full_name": "王五",
                "email": "wangwu@m.com",
                "phone": "13512345673",
                "age": "38",
                "gender": "male",
                "region": "shenzhen",
            },
            leaders=["zhangsan"],
            departments=["dept_a", "dept_b"],
        ),
        RawDataSourceUser(
            code="zhaoliu",
            properties={
                "username": "zhaoliu",
                "full_name": "赵六",
                "email": "zhaoliu@m.com",
                "phone": "13512345674",
                "age": "33",
                "gender": "female",
                "region": "tianjin",
            },
            leaders=["lisi"],
            departments=["center_aa"],
        ),
        RawDataSourceUser(
            code="liuqi",
            properties={
                "username": "liuqi",
                "full_name": "柳七",
                "email": "liuqi@m.com",
                "phone": "13512345675",
                "age": "25",
                "gender": "female",
                "region": "jiangxi",
            },
            leaders=["zhaoliu"],
            departments=["group_aaa"],
        ),
        RawDataSourceUser(
            code="maiba",
            properties={
                "username": "maiba",
                "full_name": "麦八",
                "email": "maiba@m.com",
                "phone": "13512345676",
                "age": "35",
                "gender": "male",
                "region": "xinjiang",
            },
            leaders=["lisi", "wangwu"],
            departments=["center_ab"],
        ),
        RawDataSourceUser(
            code="yangjiu",
            properties={
                "username": "yangjiu",
                "full_name": "杨九",
                "email": "yangjiu@m.com",
                "phone": "13512345677",
                "age": "40",
                "gender": "male",
                "region": "guangdong",
            },
            leaders=["wangwu"],
            departments=["center_ab"],
        ),
        RawDataSourceUser(
            code="lushi",
            properties={
                "username": "lushi",
                "full_name": "鲁十",
                "email": "lushi@m.com",
                "phone": "13512345678",
                "age": "50",
                "gender": "male",
                "region": "jiangsu",
            },
            leaders=["wangwu", "maiba"],
            departments=["group_aba", "center_ba"],
        ),
        RawDataSourceUser(
            code="linshiyi",
            properties={
                "username": "linshiyi",
                "full_name": "林十一",
                "email": "linshiyi@m.com",
                "phone": "13512345679",
                "age": "31",
                "gender": "male",
                "region": "hunan",
            },
            leaders=["lushi"],
            departments=["group_aba"],
        ),
        RawDataSourceUser(
            code="baishier",
            properties={
                "username": "baishier",
                "full_name": "白十二",
                "email": "baishier@m.com",
                "phone": "13512345670",
                "age": "30",
                "gender": "female",
                "region": "guangdong",
            },
            leaders=["lushi"],
            departments=["group_baa"],
        ),
        RawDataSourceUser(
            code="freedom",
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
            "phone": "07712345678",
            "phone_country_code": "44",
            "age": "66",
            "gender": "other",
            "region": "britain",
        },
        leaders=[],
        departments=[],
    )
