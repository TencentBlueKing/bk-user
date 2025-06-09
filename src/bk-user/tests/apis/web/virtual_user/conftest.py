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
from typing import Callable, Dict

import pytest
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.tenant.models import Tenant, TenantUser, VirtualUserAppRelation, VirtualUserOwnerRelation
from bkuser.apps.tenant.utils import TenantUserIDGenerator
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

pytestmark = pytest.mark.django_db


def _create_owners_for_test(create_real_owner: Callable, tenant: Tenant, owners: list[str]):
    for owner in owners:
        create_real_owner(tenant, owner)


@pytest.fixture
def create_real_owner() -> Callable[[Tenant, str], None]:
    def _create(tenant: Tenant, tenant_user_id: str):
        data_source, _ = DataSource.objects.get_or_create(
            type=DataSourceTypeEnum.REAL,
            owner_tenant_id=tenant.id,
            defaults={
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": LocalDataSourcePluginConfig(enable_password=False),
            },
        )
        ds_user = DataSourceUser.objects.create(
            username=tenant_user_id,
            data_source=data_source,
        )
        TenantUser.objects.create(
            id=tenant_user_id,
            data_source=data_source,
            tenant=tenant,
            data_source_user=ds_user,
        )

    return _create


@pytest.fixture
def create_virtual_user_with_relations(
    create_real_owner,
) -> Callable[[Tenant, str, list[str], list[str], str, str, str, str], TenantUser]:
    def _create(
        tenant: Tenant,
        username: str,
        app_codes: list[str],
        owners: list[str],
        full_name: str = "",
        email: str = "",
        phone: str = "",
        phone_country_code: str = "86",
    ):
        data_source, _ = DataSource.objects.get_or_create(
            type=DataSourceTypeEnum.VIRTUAL,
            owner_tenant_id=tenant.id,
            defaults={
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": LocalDataSourcePluginConfig(enable_password=False),
            },
        )

        ds_user = DataSourceUser.objects.create(
            data_source=data_source,
            code=username,
            username=username,
            full_name=full_name,
            email=email,
            phone=phone,
            phone_country_code=phone_country_code,
        )
        # 创建租户用户
        tenant_user = TenantUser.objects.create(
            id=TenantUserIDGenerator(tenant.id, data_source).gen(ds_user),
            tenant_id=tenant.id,
            data_source=data_source,
            data_source_user=ds_user,
        )
        # 创建应用关联
        if app_codes:
            VirtualUserAppRelation.objects.bulk_create(
                [
                    VirtualUserAppRelation(tenant_user=tenant_user, app_code=app_code)
                    for app_code in set(app_codes)  # 去重
                ]
            )
        # 创建责任人关联
        if owners:
            VirtualUserOwnerRelation.objects.bulk_create(
                [VirtualUserOwnerRelation(tenant_user=tenant_user, owner_id=owner) for owner in owners]
            )

        return tenant_user

    return _create


@pytest.fixture
def virtual_user_data() -> Dict:
    """预置虚拟用户测试数据"""
    return {
        "users": [
            {
                "username": "virtual_user_1",
                "full_name": "虚拟用户1",
                "app_codes": ["app1", "app2"],
                "owners": ["owner1", "owner2"],
            },
            {
                "username": "virtual_user_2",
                "full_name": "虚拟用户2",
                "app_codes": ["app3"],
                "owners": ["owner3", "owner4"],
            },
        ],
        "all_owners": ["owner1", "owner2", "owner3", "owner4"],
        "all_app_codes": ["app1", "app2", "app3"],
    }


@pytest.fixture
def prepared_owners(random_tenant, create_real_owner, virtual_user_data):
    """预创建所有的责任人"""
    for owner in virtual_user_data["all_owners"]:
        create_real_owner(random_tenant, owner)
    return virtual_user_data["all_owners"]


@pytest.fixture
def prepared_virtual_users(
    random_tenant, create_real_owner, create_virtual_user_with_relations, virtual_user_data
) -> list[TenantUser]:
    """预创建一批虚拟用户数据"""
    # 创建所有责任人
    _create_owners_for_test(create_real_owner, random_tenant, virtual_user_data["all_owners"])

    # 创建所有虚拟用户
    users = []
    for user_data in virtual_user_data["users"]:
        user = create_virtual_user_with_relations(
            tenant=random_tenant,
            username=user_data["username"],
            full_name=user_data["full_name"],
            app_codes=user_data["app_codes"],
            owners=user_data["owners"],
        )
        users.append(user)
    return users
