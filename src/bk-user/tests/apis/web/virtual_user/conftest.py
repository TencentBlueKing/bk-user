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
from typing import Callable

import pytest
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.tenant.models import Tenant, TenantUser, VirtualUserAppRelation, VirtualUserOwnerRelation
from bkuser.apps.tenant.utils import TenantUserIDGenerator
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

pytestmark = pytest.mark.django_db


@pytest.fixture
def valid_data() -> dict:
    return {
        "username": "v_user",
        "full_name": "虚拟用户",
        "email": "v@example.com",
        "phone": "13800000000",
        "phone_country_code": "86",
        "app_codes": ["app1", "app2"],
        "owners": ["real_user_1", "real_user_2"],
    }


@pytest.fixture
def create_real_owner() -> Callable[[Tenant, str], None]:
    def _create(tenant: Tenant, username: str):
        data_source, _ = DataSource.objects.get_or_create(
            type=DataSourceTypeEnum.REAL,
            owner_tenant_id=tenant.id,
            defaults={
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": LocalDataSourcePluginConfig(enable_password=False),
            },
        )
        ds_user = DataSourceUser.objects.create(
            username=username,
            data_source=data_source,
        )
        TenantUser.objects.create(
            id=TenantUserIDGenerator(tenant.id, data_source).gen(ds_user),
            data_source=data_source,
            tenant=tenant,
            data_source_user=ds_user,
        )

    return _create


@pytest.fixture
def create_virtual_user() -> Callable[[Tenant, str, str], None]:
    def _create(tenant: Tenant, username: str, full_name=""):
        data_source, _ = DataSource.objects.get_or_create(
            type=DataSourceTypeEnum.VIRTUAL,
            owner_tenant_id=tenant.id,
            defaults={
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": LocalDataSourcePluginConfig(enable_password=False),
            },
        )
        ds_user = DataSourceUser.objects.create(
            username=username,
            data_source=data_source,
            full_name=full_name,
        )
        TenantUser.objects.create(
            id=TenantUserIDGenerator(tenant.id, data_source).gen(ds_user),
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
            owner_mapping = dict(
                TenantUser.objects.filter(
                    data_source__type=DataSourceTypeEnum.REAL, data_source_user__username__in=owners
                ).values_list("data_source_user__username", "id")
            )
            VirtualUserOwnerRelation.objects.bulk_create(
                [
                    VirtualUserOwnerRelation(tenant_user=tenant_user, owner_id=owner_mapping[owner])
                    for owner in owners
                    if owner in owner_mapping
                ]
            )

        return tenant_user

    return _create
