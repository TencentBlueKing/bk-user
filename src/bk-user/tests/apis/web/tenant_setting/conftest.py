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
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import TenantUserCustomField

from tests.test_utils.tenant import sync_users_depts_to_tenant

pytestmark = pytest.mark.django_db


@pytest.fixture
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


@pytest.fixture
def _init_tenant_users_depts(random_tenant, full_local_data_source) -> None:
    """初始化租户部门 & 租户用户"""
    sync_users_depts_to_tenant(random_tenant, full_local_data_source)


@pytest.fixture
def _create_custom_fields(random_tenant, full_local_data_source):
    custom_field_data = [
        {
            "tenant": random_tenant,
            "name": "test_num",
            "display_name": "数字测试",
            "data_type": UserFieldDataType.NUMBER,
            "required": True,
            "default": 0,
            "options": [],
        },
        {
            "tenant": random_tenant,
            "name": "test_str",
            "display_name": "字符测试",
            "data_type": UserFieldDataType.STRING,
            "required": True,
            "default": "test",
            "options": [],
            "unique": True,
        },
        {
            "tenant": random_tenant,
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
    ]
    custom_field_list = [TenantUserCustomField(**field) for field in custom_field_data]
    TenantUserCustomField.objects.bulk_create(custom_field_list)

    # 初始化数据源用户的自定义字段
    data_source_users = DataSourceUser.objects.filter(data_source=full_local_data_source)
    for data_source_user in data_source_users:
        data_source_user.extras = {
            "test_num": data_source_user.phone,
            "test_str": data_source_user.username,
            "test_enum": data_source_user.full_name,
        }
        data_source_user.save()
