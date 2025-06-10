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
from typing import Dict

import pytest
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.tenant.models import Tenant, TenantUser, VirtualUserAppRelation, VirtualUserOwnerRelation
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

pytestmark = pytest.mark.django_db


def _create_data_source(tenant: Tenant, data_source_type: DataSourceTypeEnum) -> DataSource:
    data_source, _ = DataSource.objects.get_or_create(
        type=data_source_type,
        owner_tenant_id=tenant.id,
        defaults={
            "plugin_id": DataSourcePluginEnum.LOCAL,
            "plugin_config": LocalDataSourcePluginConfig(enable_password=False),
        },
    )
    return data_source


def _create_owner(tenant: Tenant, tenant_user_id: str):
    data_source = _create_data_source(tenant, DataSourceTypeEnum.REAL)
    ds_user = DataSourceUser.objects.create(
        username=tenant_user_id,
        data_source=data_source,
        code=tenant_user_id,
        full_name=tenant_user_id,
    )
    TenantUser.objects.create(
        id=tenant_user_id,
        data_source=data_source,
        tenant=tenant,
        data_source_user=ds_user,
    )


@pytest.fixture
def virtual_user_data() -> Dict:
    return {
        "users": [
            {
                "tenant_user_id": "virtual_user_id_1",
                "username": "virtual_user_1",
                "full_name": "测试用户1",
                "app_codes": ["app1", "app2"],
                "owners": ["owner1", "owner2"],
            },
            {
                "tenant_user_id": "virtual_user_id_2",
                "username": "virtual_user_2",
                "full_name": "测试用户2",
                "app_codes": ["app3"],
                "owners": ["owner3"],
            },
            {
                "tenant_user_id": "virtual_user_id_3",
                "username": "virtual_user_3",
                "full_name": "测试用户3",
                "app_codes": ["app1", "app3", "app4"],
                "owners": ["owner1", "owner4"],
            },
        ],
        "all_owners": ["owner1", "owner2", "owner3", "owner4", "owner5", "owner6"],
        "all_app_codes": ["app1", "app2", "app3", "app4"],
    }


@pytest.fixture
def _init_virtual_user(random_tenant, virtual_user_data):
    data = virtual_user_data
    data_source = _create_data_source(random_tenant, DataSourceTypeEnum.VIRTUAL)
    for owner in data["all_owners"]:
        _create_owner(random_tenant, owner)
    for user_data in data["users"]:
        data_source_user = DataSourceUser.objects.create(
            username=user_data["username"],
            code=user_data["username"],
            full_name=user_data["full_name"],
            data_source=data_source,
        )
        tenant_user = TenantUser.objects.create(
            id=user_data["tenant_user_id"],
            tenant=random_tenant,
            data_source=data_source,
            data_source_user=data_source_user,
        )
        for app_code in user_data["app_codes"]:
            VirtualUserAppRelation.objects.create(
                tenant_user=tenant_user,
                app_code=app_code,
            )
        for owner_id in user_data["owners"]:
            owner = TenantUser.objects.get(id=owner_id)
            VirtualUserOwnerRelation.objects.create(
                tenant_user=tenant_user,
                owner=owner,
            )
