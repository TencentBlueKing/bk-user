# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import pytest
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.tenant.constants import CollaborationScopeType, CollaborationStrategyStatus
from bkuser.apps.tenant.models import CollaborationStrategy
from bkuser.plugins.general.models import GeneralDataSourcePluginConfig
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

from tests.test_utils.data_source import init_data_source_users_depts_and_relations
from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import sync_users_depts_to_tenant

pytestmark = pytest.mark.django_db


@pytest.fixture()
def local_data_source(default_tenant, local_ds_plugin_cfg, local_ds_plugin) -> DataSource:
    """默认租户的本地数据源"""
    data_source = DataSource.objects.create(
        owner_tenant_id=default_tenant.id,
        type=DataSourceTypeEnum.REAL,
        plugin=local_ds_plugin,
        plugin_config=LocalDataSourcePluginConfig(**local_ds_plugin_cfg),
    )
    init_data_source_users_depts_and_relations(data_source)
    sync_users_depts_to_tenant(default_tenant, data_source)
    return data_source


@pytest.fixture()
def collaboration_data_source(default_tenant, random_tenant, general_ds_plugin_cfg, general_ds_plugin) -> DataSource:
    """向默认租户进行同步的通用 HTTP 数据源"""
    data_source = DataSource.objects.create(
        owner_tenant_id=random_tenant.id,
        type=DataSourceTypeEnum.REAL,
        plugin=general_ds_plugin,
        plugin_config=GeneralDataSourcePluginConfig(**general_ds_plugin_cfg),
        sync_config={"sync_period": 60},
    )
    init_data_source_users_depts_and_relations(data_source)

    CollaborationStrategy.objects.create(
        name=generate_random_string(),
        source_tenant=random_tenant,
        target_tenant=default_tenant,
        source_status=CollaborationStrategyStatus.ENABLED,
        target_status=CollaborationStrategyStatus.ENABLED,
        source_config={
            "organization_scope_type": CollaborationScopeType.ALL,
            "organization_scope_config": {},
            "field_scope_type": CollaborationScopeType.ALL,
            "field_scope_config": {},
        },
        target_config={
            "organization_scope_type": CollaborationScopeType.ALL,
            "organization_scope_config": {},
            # 暂时不考虑自定义字段的字段映射
            "field_mapping": [],
        },
    )

    sync_users_depts_to_tenant(default_tenant, data_source)
    return data_source
