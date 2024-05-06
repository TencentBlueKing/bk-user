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
import pytest
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.tenant.models import Tenant
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

from tests.test_utils.data_source import init_data_source_users_depts_and_relations
from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import create_tenant, sync_users_depts_to_tenant


@pytest.fixture()
def _init_tenant_users_depts(random_tenant, full_local_data_source) -> None:
    """初始化租户部门 & 租户用户"""
    sync_users_depts_to_tenant(random_tenant, full_local_data_source)


@pytest.fixture()
def collaboration_tenant() -> Tenant:
    """创建随机的协同租户"""
    return create_tenant(generate_random_string())


@pytest.fixture()
def _init_collaboration_users_depts(
    random_tenant,
    collaboration_tenant,
    local_ds_plugin,
    local_ds_plugin_cfg,
) -> None:
    """初始化协同所得的租户部门 & 租户用户（协同租户同步到当前随机租户）"""
    data_source = DataSource.objects.create(
        owner_tenant_id=collaboration_tenant.id,
        type=DataSourceTypeEnum.REAL,
        plugin=local_ds_plugin,
        plugin_config=LocalDataSourcePluginConfig(**local_ds_plugin_cfg),
    )
    init_data_source_users_depts_and_relations(data_source)
    sync_users_depts_to_tenant(random_tenant, data_source)
