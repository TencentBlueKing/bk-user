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
from bkuser.apps.tenant.constants import TenantUserIdRuleEnum
from bkuser.apps.tenant.models import (
    TenantUser,
    TenantUserIDGenerateConfig,
    VirtualUserAppRelation,
    VirtualUserOwnerRelation,
)

from tests.test_utils.tenant import sync_users_depts_to_tenant

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
def _init_virtual_user(random_tenant, _init_tenant_users_depts, bare_virtual_data_source) -> None:
    # virtual_user_1
    data_source_user_1 = DataSourceUser.objects.create(
        username="virtual_user_1",
        code="virtual_user_1",
        full_name="虚拟用户1",
        data_source=bare_virtual_data_source,
    )
    virtual_user_1 = TenantUser.objects.create(
        id="virtual_user_1",
        tenant=random_tenant,
        data_source_user=data_source_user_1,
        data_source=bare_virtual_data_source,
    )
    VirtualUserAppRelation.objects.bulk_create(
        [
            VirtualUserAppRelation(tenant_user=virtual_user_1, app_code="app1"),
            VirtualUserAppRelation(tenant_user=virtual_user_1, app_code="app2"),
        ]
    )
    VirtualUserOwnerRelation.objects.bulk_create(
        [
            VirtualUserOwnerRelation(tenant_user=virtual_user_1, owner_id="zhangsan"),
            VirtualUserOwnerRelation(tenant_user=virtual_user_1, owner_id="lisi"),
        ]
    )
    # virtual_user_2
    data_source_user_2 = DataSourceUser.objects.create(
        username="virtual_user_2",
        code="virtual_user_2",
        full_name="虚拟用户2",
        data_source=bare_virtual_data_source,
    )
    virtual_user_2 = TenantUser.objects.create(
        id="virtual_user_2",
        tenant=random_tenant,
        data_source_user=data_source_user_2,
        data_source=bare_virtual_data_source,
    )
    VirtualUserAppRelation.objects.bulk_create(
        [
            VirtualUserAppRelation(tenant_user=virtual_user_2, app_code="app3"),
        ]
    )
    VirtualUserOwnerRelation.objects.bulk_create(
        [
            VirtualUserOwnerRelation(tenant_user=virtual_user_2, owner_id="lisi"),
            VirtualUserOwnerRelation(tenant_user=virtual_user_2, owner_id="wangwu"),
            VirtualUserOwnerRelation(tenant_user=virtual_user_2, owner_id="zhaoliu"),
            VirtualUserOwnerRelation(tenant_user=virtual_user_2, owner_id="liuqi"),
        ]
    )
    # virtual_user_3
    data_source_user_3 = DataSourceUser.objects.create(
        username="virtual_user_3",
        code="virtual_user_3",
        full_name="虚拟用户3",
        data_source=bare_virtual_data_source,
    )
    virtual_user_3 = TenantUser.objects.create(
        id="virtual_user_3",
        tenant=random_tenant,
        data_source_user=data_source_user_3,
        data_source=bare_virtual_data_source,
    )
    VirtualUserAppRelation.objects.bulk_create(
        [
            VirtualUserAppRelation(tenant_user=virtual_user_3, app_code="app4"),
            VirtualUserAppRelation(tenant_user=virtual_user_3, app_code="app5"),
        ]
    )
    VirtualUserOwnerRelation.objects.bulk_create(
        [
            VirtualUserOwnerRelation(tenant_user=virtual_user_3, owner_id="maiba"),
            VirtualUserOwnerRelation(tenant_user=virtual_user_3, owner_id="yangjiu"),
            VirtualUserOwnerRelation(tenant_user=virtual_user_3, owner_id="lushi"),
        ]
    )
