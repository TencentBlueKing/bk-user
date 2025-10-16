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
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourcePlugin, DataSourceUser
from bkuser.apps.tenant.constants import TenantUserIdRuleEnum
from bkuser.apps.tenant.models import (
    TenantUser,
    TenantUserIDGenerateConfig,
)
from bkuser.biz.virtual_user import VirtualUserHandler
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

from tests.test_utils.tenant import create_tenant, sync_users_depts_to_tenant

pytestmark = pytest.mark.django_db


@pytest.fixture
def _init_tenant_users_depts(random_tenant, full_local_data_source) -> None:
    """初始化租户部门 & 租户用户"""
    # 这里修改 TenantUserIDGenerateConfig 方便测试
    TenantUserIDGenerateConfig.objects.create(
        data_source=full_local_data_source,
        rule=TenantUserIdRuleEnum.USERNAME,
        target_tenant_id=full_local_data_source.owner_tenant_id,
    )
    sync_users_depts_to_tenant(random_tenant, full_local_data_source)


@pytest.fixture
def _init_virtual_users(random_tenant, _init_tenant_users_depts, bare_virtual_data_source) -> None:
    """初始化虚拟用户"""
    virtual_user_data = [
        {
            "username": "virtual_user_1",
            "full_name": "虚拟用户_1",
            "app_codes": ["app1", "app2"],
            "owners": ["zhangsan", "lisi"],
        },
        {
            "username": "virtual_user_2",
            "full_name": "虚拟用户_2",
            "app_codes": ["app3"],
            "owners": ["lisi", "wangwu", "zhaoliu", "liuqi"],
        },
        {
            "username": "virtual_user_3",
            "full_name": "虚拟用户_3",
            "app_codes": ["app4", "app5"],
            "owners": ["maiba", "yangjiu", "lushi"],
        },
    ]

    for virtual_user in virtual_user_data:
        username = virtual_user["username"]

        # 创建数据源用户
        data_source_user = DataSourceUser.objects.create(
            username=username,
            code=username,
            full_name=virtual_user["full_name"],
            data_source=bare_virtual_data_source,
        )
        # 创建租户用户
        tenant_user = TenantUser.objects.create(
            id=username,
            tenant=random_tenant,
            data_source_user=data_source_user,
            data_source=bare_virtual_data_source,
        )
        # 创建 app_code 关联
        VirtualUserHandler.add_app_codes(tenant_user, list(virtual_user["app_codes"]))
        # 创建责任人关联
        VirtualUserHandler.add_owners(tenant_user, list(virtual_user["owners"]))


@pytest.fixture
def _init_cross_tenant_user() -> None:
    tenant = create_tenant("cross_tenant_id")
    data_source, _ = DataSource.objects.get_or_create(
        type=DataSourceTypeEnum.REAL,
        owner_tenant_id=tenant.id,
        defaults={
            "plugin": DataSourcePlugin.objects.get(id=DataSourcePluginEnum.LOCAL),
            "plugin_config": LocalDataSourcePluginConfig(enable_password=False),
        },
    )
    ds_user = DataSourceUser.objects.create(
        username="cross_tenant_ds_user",
        code="cross_tenant_ds_user",
        data_source=data_source,
        full_name="cross_tenant_ds_user",
    )
    TenantUser.objects.create(
        tenant=tenant,
        data_source_user=ds_user,
        data_source=data_source,
        id="cross_tenant_user",
    )
