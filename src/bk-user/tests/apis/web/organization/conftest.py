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
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.tenant.constants import CollaborationScopeType, CollaborationStrategyStatus, UserFieldDataType
from bkuser.apps.tenant.models import CollaborationStrategy, Tenant, TenantUserCustomField
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

from tests.test_utils.data_source import init_data_source_users_depts_and_relations
from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import create_tenant, sync_users_depts_to_tenant


def _create_tenant_custom_fields(tenant: Tenant) -> List[TenantUserCustomField]:
    """
    创建测试用的租户用户自定义字段

    以租户 ID 为前缀，分别是 age(number), gender(enum), region(string)
    """
    age_field = TenantUserCustomField.objects.create(
        tenant=tenant,
        name=f"{tenant.id}_age",
        display_name="年龄",
        data_type=UserFieldDataType.NUMBER,
        required=True,
        default=0,
    )
    gender_field = TenantUserCustomField.objects.create(
        tenant=tenant,
        name=f"{tenant.id}_gender",
        display_name="性别",
        data_type=UserFieldDataType.ENUM,
        required=True,
        default="male",
        options=[
            {"id": "male", "value": "男"},
            {"id": "female", "value": "女"},
            {"id": "other", "value": "其他"},
        ],
    )
    region_field = TenantUserCustomField.objects.create(
        tenant=tenant,
        name=f"{tenant.id}_region",
        display_name="籍贯",
        data_type=UserFieldDataType.STRING,
        required=True,
        default="china",
    )
    hobbies_field = TenantUserCustomField.objects.create(
        tenant=tenant,
        name=f"{tenant.id}_hobbies",
        display_name="爱好",
        data_type=UserFieldDataType.MULTI_ENUM,
        required=True,
        default=["singing", "reading"],
        options=[
            {"id": "singing", "value": "唱歌"},
            {"id": "shopping", "value": "购物"},
            {"id": "reading", "value": "阅读"},
            {"id": "dancing", "value": "跳舞"},
            {"id": "gaming", "value": "游戏"},
            {"id": "studying", "value": "学习"},
            {"id": "driving", "value": "驾驶"},
            {"id": "eating", "value": "吃饭"},
            {"id": "collecting", "value": "采集"},
            {"id": "sleeping", "value": "睡觉"},
            {"id": "traveling", "value": "旅游"},
            {"id": "hacking", "value": "骇入"},
            {"id": "hunting", "value": "狩猎"},
            {"id": "other", "value": "其他"},
        ],
    )
    return [age_field, gender_field, region_field, hobbies_field]


@pytest.fixture()
def random_tenant_custom_fields(random_tenant) -> List[TenantUserCustomField]:
    """随机租户的自定义字段"""
    return _create_tenant_custom_fields(random_tenant)


@pytest.fixture()
def collaboration_tenant_custom_fields(collaboration_tenant) -> List[TenantUserCustomField]:
    """协同租户的自定义字段"""
    return _create_tenant_custom_fields(collaboration_tenant)


@pytest.fixture()
def _init_tenant_users_depts(random_tenant, full_local_data_source, random_tenant_custom_fields) -> None:
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
    random_tenant_custom_fields,
    collaboration_tenant_custom_fields,
    local_ds_plugin,
    local_ds_plugin_cfg,
) -> None:
    """初始化协同所得的租户部门 & 租户用户（协同租户同步到当前随机租户）"""
    # 协同策略
    CollaborationStrategy.objects.create(
        name=generate_random_string(),
        source_tenant=collaboration_tenant,
        target_tenant=random_tenant,
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
            "field_mapping": [
                {
                    "source_field": f"{collaboration_tenant.id}_{field}",
                    "mapping_operation": "direct",
                    "target_field": f"{random_tenant.id}_{field}",
                }
                for field in ["age", "gender", "region"]
            ],
        },
    )
    data_source = DataSource.objects.create(
        owner_tenant_id=collaboration_tenant.id,
        type=DataSourceTypeEnum.REAL,
        plugin=local_ds_plugin,
        plugin_config=LocalDataSourcePluginConfig(**local_ds_plugin_cfg),
    )
    init_data_source_users_depts_and_relations(data_source)
    sync_users_depts_to_tenant(random_tenant, data_source)
