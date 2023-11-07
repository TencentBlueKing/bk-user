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
from bkuser.apps.data_source.models import DataSource, DataSourceDepartment, DataSourceUser
from bkuser.apps.natural_user.models import NaturalUser
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.utils.uuid import generate_uuid

from tests.test_utils.data_source import (
    create_data_source_departments_with_relations,
    create_data_source_users_with_relations,
)
from tests.test_utils.helpers import generate_random_string
from tests.test_utils.natural_user import create_natural_user_with_bind_data_source_users
from tests.test_utils.tenant import create_tenant_departments, create_tenant_users

pytestmark = pytest.mark.django_db


@pytest.fixture()
def data_source_departments(default_tenant) -> List[DataSourceDepartment]:
    """
    根据测试数据源，创建测试数据源部门
    """
    # FIXME (su) 数据源尽量随机，不要使用默认数据源，本文件有多处需要修改
    data_source = DataSource.objects.get(
        owner_tenant_id=default_tenant.id,
        name=f"{default_tenant.id}-default-local",
        plugin_id=DataSourcePluginEnum.LOCAL,
    )
    return create_data_source_departments_with_relations(data_source)


@pytest.fixture()
def data_source_users(default_tenant, data_source_departments) -> List[DataSourceUser]:
    """
    根据测试数据源，创建测试数据源用户
    """
    data_source = DataSource.objects.get(
        owner_tenant_id=default_tenant.id,
        name=f"{default_tenant.id}-default-local",
        plugin_id=DataSourcePluginEnum.LOCAL,
    )
    return create_data_source_users_with_relations(data_source, data_source_departments)


@pytest.fixture()
def natural_user(data_source_users) -> NaturalUser:
    """
    根据测试数据源用户，创建自然人
    """
    return create_natural_user_with_bind_data_source_users(data_source_users)


@pytest.fixture()
def tenant_users(default_tenant, data_source_users) -> List[TenantUser]:
    """
    根据测试数据源用户，创建租户用户
    """
    return create_tenant_users(default_tenant, data_source_users)


@pytest.fixture()
def random_tenant_users(random_tenant, data_source_users) -> List[TenantUser]:
    """
    根据测试数据源用户，创建随机租户-用户
    """
    return create_tenant_users(random_tenant, data_source_users)


@pytest.fixture()
def tenant_departments(default_tenant, data_source_departments) -> List[TenantDepartment]:
    """
    根据测试数据源部门，创建租户部门
    """
    return create_tenant_departments(default_tenant, data_source_departments)


@pytest.fixture()
def random_tenant_departments(random_tenant, data_source_departments) -> List[TenantDepartment]:
    """
    根据测试数据源部门，创建随机租户-部门
    """
    return create_tenant_departments(random_tenant, data_source_departments)


@pytest.fixture()
def additional_data_source_user(default_tenant) -> DataSourceUser:
    """
    根据测试数据源，创建额外的数据源用户
    """
    data_source = DataSource.objects.get(
        owner_tenant_id=default_tenant.id,
        name=f"{default_tenant.id}-default-local",
        plugin_id=DataSourcePluginEnum.LOCAL,
    )
    return DataSourceUser.objects.create(
        full_name=generate_random_string(),
        username=generate_random_string,
        email=f"{generate_random_string()}@qq.com",
        phone="13123456789",
        data_source=data_source,
    )


@pytest.fixture()
def additional_tenant_user(random_tenant, additional_data_source_user) -> TenantUser:
    """
    根据独立数据源用户，创建额外的租户用户
    """
    return TenantUser.objects.create(
        data_source_user=additional_data_source_user,
        data_source=additional_data_source_user.data_source,
        tenant=random_tenant,
        id=generate_uuid(),
    )


@pytest.fixture()
def additional_natural_user(additional_data_source_user) -> NaturalUser:
    """
    创建额外的自然人
    """
    return create_natural_user_with_bind_data_source_users([additional_data_source_user])
