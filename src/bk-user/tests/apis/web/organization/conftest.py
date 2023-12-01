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
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import TenantDepartment, TenantUser, TenantUserCustomField
from bkuser.plugins.constants import DataSourcePluginEnum

from tests.test_utils.data_source import (
    create_data_source_departments_with_relations,
    create_data_source_users_with_relations,
)
from tests.test_utils.tenant import create_tenant_departments, create_tenant_users

pytestmark = pytest.mark.django_db


@pytest.fixture()
def data_source(default_tenant):
    return DataSource.objects.get(
        owner_tenant_id=default_tenant.id,
        name=f"{default_tenant.id}-default-local",
        plugin_id=DataSourcePluginEnum.LOCAL,
    )


@pytest.fixture()
def data_source_departments(data_source) -> List[DataSourceDepartment]:
    """
    根据测试数据源，创建测试数据源部门
    """
    return create_data_source_departments_with_relations(data_source)


@pytest.fixture()
def data_source_users(data_source_departments, data_source) -> List[DataSourceUser]:
    """
    根据测试数据源，创建测试数据源用户
    """
    return create_data_source_users_with_relations(data_source, data_source_departments)


@pytest.fixture()
def tenant_users(default_tenant, data_source_users) -> List[TenantUser]:
    """
    根据测试数据源用户，创建租户用户
    """
    return create_tenant_users(default_tenant, data_source_users)


@pytest.fixture()
def tenant_departments(default_tenant, data_source_departments) -> List[TenantDepartment]:
    """
    根据测试数据源部门，创建租户部门
    """
    return create_tenant_departments(default_tenant, data_source_departments)


@pytest.fixture()
def custom_fields(default_tenant):
    custom_field_data = [
        {
            "tenant": default_tenant,
            "name": "test_num",
            "display_name": "数字测试",
            "data_type": UserFieldDataType.NUMBER,
            "required": True,
            "default": 0,
            "options": [],
        },
        {
            "tenant": default_tenant,
            "name": "test_str",
            "display_name": "字符测试",
            "data_type": UserFieldDataType.STRING,
            "required": True,
            "default": "test",
            "options": [],
        },
        {
            "tenant": default_tenant,
            "name": "test_enum",
            "display_name": "test_enum",
            "data_type": UserFieldDataType.ENUM,
            "required": True,
            "default": "test_a",
            "options": [
                {"id": "test_a", "value": "test_a"},
                {"id": "test_b", "value": "test_b"},
            ],
        },
        {
            "tenant": default_tenant,
            "name": "test_multi_enum",
            "display_name": "test_multi_enum",
            "data_type": UserFieldDataType.MULTI_ENUM,
            "required": True,
            "default": ["test_a", "test_b"],
            "options": [
                {"id": "test_a", "value": "test_a"},
                {"id": "test_b", "value": "test_b"},
                {"id": "test_c", "value": "test_c"},
            ],
        },
    ]
    custom_field_list = [TenantUserCustomField(**field) for field in custom_field_data]
    TenantUserCustomField.objects.bulk_create(custom_field_list)
    return TenantUserCustomField.objects.filter(tenant=default_tenant)
