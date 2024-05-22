"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from typing import Dict

import pytest
from bkuser.apps.tenant.constants import CollaborationScopeType, UserFieldDataType
from bkuser.apps.tenant.models import CollaborationStrategy, Tenant, TenantUserCustomField

from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import create_tenant


@pytest.fixture()
def collaboration_tenant() -> Tenant:
    """创建随机的协同租户"""
    return create_tenant(generate_random_string())


@pytest.fixture()
def strategy_source_config() -> Dict:
    return {
        "organization_scope_type": CollaborationScopeType.ALL,
        "organization_scope_config": {},
        "field_scope_type": CollaborationScopeType.ALL,
        "field_scope_config": {},
    }


@pytest.fixture()
def strategy_target_config(random_tenant, collaboration_tenant) -> Dict:
    return {
        "organization_scope_type": CollaborationScopeType.ALL,
        "organization_scope_config": {},
        "field_mapping": [
            {
                "source_field": f"{collaboration_tenant.id}-{field}",
                "mapping_operation": "direct",
                "target_field": f"{random_tenant.id}-{field}",
            }
            for field in ["age", "gender", "region"]
        ],
    }


def _create_strategy(
    source_tenant: Tenant, target_tenant: Tenant, source_config: Dict, target_config: Dict
) -> CollaborationStrategy:
    return CollaborationStrategy.objects.create(
        name=generate_random_string(),
        source_tenant=source_tenant,
        target_tenant=target_tenant,
        source_config=source_config,
        target_config=target_config,
    )


@pytest.fixture()
def collaborate_to_strategy(
    random_tenant, collaboration_tenant, strategy_source_config, strategy_target_config
) -> CollaborationStrategy:
    """创建协同策略（本租户分享出去的）"""
    return _create_strategy(random_tenant, collaboration_tenant, strategy_source_config, strategy_target_config)


@pytest.fixture()
def collaborate_from_strategy(
    random_tenant, collaboration_tenant, strategy_source_config, strategy_target_config
) -> CollaborationStrategy:
    """创建协同策略（被其他租户分享进来的）"""
    return _create_strategy(collaboration_tenant, random_tenant, strategy_source_config, strategy_target_config)


def _create_tenant_custom_fields(tenant: Tenant) -> None:
    """
    创建测试用的租户用户自定义字段

    以租户 ID 为前缀，分别是 age(number), gender(enum), region(string)
    """
    TenantUserCustomField.objects.create(
        tenant=tenant,
        name=f"{tenant.id}-age",
        display_name="年龄",
        data_type=UserFieldDataType.NUMBER,
        required=False,
        default=0,
    )
    TenantUserCustomField.objects.create(
        tenant=tenant,
        name=f"{tenant.id}-gender",
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
    TenantUserCustomField.objects.create(
        tenant=tenant,
        name=f"{tenant.id}-region",
        display_name="籍贯",
        data_type=UserFieldDataType.STRING,
        required=True,
        default="china",
    )


@pytest.fixture()
def _init_random_tenant_custom_fields(random_tenant):
    _create_tenant_custom_fields(random_tenant)


@pytest.fixture()
def _init_collaboration_tenant_custom_fields(collaboration_tenant):
    _create_tenant_custom_fields(collaboration_tenant)
