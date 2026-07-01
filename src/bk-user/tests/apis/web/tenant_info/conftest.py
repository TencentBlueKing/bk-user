# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
from bkuser.apps.tenant.models import TenantManager, TenantUser

from tests.test_utils.tenant import sync_users_depts_to_tenant


@pytest.fixture
def _init_tenant_users_depts(random_tenant, full_local_data_source) -> None:
    """初始化租户部门 & 租户用户"""
    sync_users_depts_to_tenant(random_tenant, full_local_data_source)


@pytest.fixture
def real_tenant_user(random_tenant, _init_tenant_users_depts) -> TenantUser:
    """获取一个实名租户用户（lisi）"""
    return TenantUser.objects.get(data_source_user__username="lisi", tenant=random_tenant)


@pytest.fixture
def another_real_tenant_user(random_tenant, _init_tenant_users_depts) -> TenantUser:
    """获取另一个实名租户用户（wangwu）"""
    return TenantUser.objects.get(data_source_user__username="wangwu", tenant=random_tenant)


@pytest.fixture
def real_manager(random_tenant, real_tenant_user) -> TenantManager:
    """将实名用户设置为管理员"""
    manager, _ = TenantManager.objects.get_or_create(
        tenant=random_tenant,
        tenant_user=real_tenant_user,
    )
    return manager


@pytest.fixture
def another_real_manager(random_tenant, another_real_tenant_user) -> TenantManager:
    """将另一个实名用户设置为管理员"""
    manager, _ = TenantManager.objects.get_or_create(
        tenant=random_tenant,
        tenant_user=another_real_tenant_user,
    )
    return manager
