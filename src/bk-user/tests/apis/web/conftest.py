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
from bkuser.apps.data_source.constants import DataSourcePluginEnum
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceUser,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantUser

from tests.test_utils.data_source import (
    create_data_source_departments_with_relations,
    create_data_source_users_with_relations,
)
from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import create_tenant_departments, create_tenant_users


@pytest.fixture()
def local_data_source(default_tenant) -> DataSource:
    """
    创建测试数据源
    """
    return DataSource.objects.create(
        name=generate_random_string(), owner_tenant_id=default_tenant, plugin_id=DataSourcePluginEnum.LOCAL
    )


@pytest.fixture()
def local_data_source_departments(local_data_source) -> List[DataSourceDepartment]:
    """
    创建测试数据源部门，并以首个对象作为父部门
    """
    return create_data_source_departments_with_relations(local_data_source)


@pytest.fixture()
def local_data_source_users(local_data_source, local_data_source_departments) -> List[DataSourceUser]:
    """
    创建测试数据源用户， 并以首个对象作为leader, 随机关联部门
    """
    return create_data_source_users_with_relations(local_data_source, local_data_source_departments)


@pytest.fixture()
def tenant_users(default_tenant, local_data_source_users) -> List[TenantUser]:
    """
    根据测试数据源用户，创建租户用户
    """
    return create_tenant_users(default_tenant, local_data_source_users)


@pytest.fixture()
def tenant_departments(default_tenant, local_data_source, local_data_source_departments) -> List[TenantDepartment]:
    """
    根据测试数据源部门，创建租户部门
    """
    return create_tenant_departments(default_tenant, local_data_source_departments)
