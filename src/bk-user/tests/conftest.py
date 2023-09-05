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
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceUser,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.auth.models import User

from tests.test_utils.auth import create_user
from tests.test_utils.data_source import (
    create_data_source_departments_with_relationship,
    create_data_source_users_with_relationship,
)
from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import create_tenant, create_tenant_departments, create_tenant_users


@pytest.fixture()
def default_tenant() -> str:
    """初始化默认租户"""
    return create_tenant().id


@pytest.fixture()
def random_tenant() -> str:
    """生成随机租户"""
    return create_tenant(generate_random_string()).id


@pytest.fixture()
def bk_user(default_tenant: str) -> User:
    """生成随机用户"""
    return create_user()


@pytest.fixture()
def local_data_source(default_tenant: str) -> DataSource:
    """
    创建测试数据源
    """
    return DataSource.objects.create(name="local_data_source", owner_tenant_id=default_tenant, plugin_id="local")


@pytest.fixture()
def local_data_source_departments(local_data_source: DataSource) -> List[DataSourceDepartment]:
    """
    创建测试数据源部门，并以首个对象作为父部门
    """
    return create_data_source_departments_with_relationship(local_data_source.id)


@pytest.fixture()
def local_data_source_users(
    local_data_source: DataSource, local_data_source_departments: List[DataSourceDepartment]
) -> List[DataSourceUser]:
    """
    创建测试数据源用户， 并以首个对象作为leader, 随机关联部门
    """
    return create_data_source_users_with_relationship(
        local_data_source.id, [department.id for department in local_data_source_departments]
    )


@pytest.fixture()
def default_tenant_users(
    default_tenant: str, local_data_source: DataSource, local_data_source_users: List[DataSourceUser]
) -> List[TenantUser]:
    """
    根据测试数据源用户，创建租户用户
    """
    return create_tenant_users(default_tenant, local_data_source.id, [user.id for user in local_data_source_users])


@pytest.fixture()
def default_tenant_departments(
    default_tenant: str, local_data_source: DataSource, local_data_source_departments: List[DataSourceDepartment]
) -> List[TenantDepartment]:
    """
    根据测试数据源部门，创建租户部门
    """
    return create_tenant_departments(
        default_tenant, local_data_source.id, [department.id for department in local_data_source_departments]
    )
