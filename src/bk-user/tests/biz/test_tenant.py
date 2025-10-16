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
from bkuser.apps.data_source.models import DataSource, LocalDataSourceIdentityInfo
from bkuser.apps.tenant.constants import TenantStatus
from bkuser.apps.tenant.models import (
    Tenant,
    TenantManager,
    TenantUser,
    TenantUserDisplayNameExpressionConfig,
    TenantUserValidityPeriodConfig,
)
from bkuser.biz.tenant import BuiltinManagerInfo, TenantCreator, TenantInfo, VirtualUserInfo
from bkuser.plugins.constants import DataSourcePluginEnum

pytestmark = pytest.mark.django_db


class TestTenantCreator:
    def test_create_tenant_base(self):
        """测试创建租户基础信息"""
        info = TenantInfo(
            tenant_id="test-tenant",
            tenant_name="Test Tenant",
            logo="test-logo",
            status=TenantStatus.ENABLED,
            is_default=False,
        )

        tenant = TenantCreator.create_tenant_base(info)

        assert tenant.id == "test-tenant"
        assert tenant.name == "Test Tenant"
        assert tenant.logo == "test-logo"
        assert tenant.status == TenantStatus.ENABLED
        assert not tenant.is_default

    def test_init_tenant_default_settings(self):
        """测试初始化租户默认配置"""
        tenant = Tenant.objects.create(id="test-tenant", name="Test Tenant")

        TenantCreator.create_tenant_default_settings(tenant)

        # 验证配置已创建
        assert TenantUserValidityPeriodConfig.objects.filter(tenant=tenant).exists()
        assert TenantUserDisplayNameExpressionConfig.objects.filter(tenant=tenant).exists()

    def test_create_simple_builtin_data_source(self):
        """测试创建简单的内建管理数据源"""
        data_source = TenantCreator.create_builtin_management_data_source("test-tenant")

        assert data_source.type == DataSourceTypeEnum.BUILTIN_MANAGEMENT
        assert data_source.owner_tenant_id == "test-tenant"

    def test_create_complex_builtin_data_source(self):
        """测试创建复杂的内建管理数据源"""
        data_source = TenantCreator.create_builtin_management_data_source(
            "test-tenant", fixed_password="Passwd-123456!", notification_methods=["email"]
        )

        assert data_source.type == DataSourceTypeEnum.BUILTIN_MANAGEMENT
        assert data_source.owner_tenant_id == "test-tenant"

    def test_create_virtual_data_source(self):
        """测试创建虚拟数据源"""
        data_source = TenantCreator.create_virtual_data_source("test-tenant")

        assert data_source.type == DataSourceTypeEnum.VIRTUAL
        assert data_source.owner_tenant_id == "test-tenant"

    def test_create_builtin_manager(self):
        """测试创建内置管理员"""
        tenant = Tenant.objects.create(id="test-tenant", name="Test Tenant")

        data_source = TenantCreator.create_builtin_management_data_source(tenant.id)

        tenant_user = TenantCreator.create_builtin_manager(
            tenant=tenant,
            data_source=data_source,
            built_manager=BuiltinManagerInfo(
                username="admin",
                password="Passwd-123456!",
                email="admin@test.com",
                phone="13800138000",
                phone_country_code="86",
            ),
        )

        assert tenant_user.tenant == tenant
        assert tenant_user.data_source == data_source

        # 验证数据源用户
        data_source_user = tenant_user.data_source_user
        assert data_source_user.username == "admin"
        assert data_source_user.email == "admin@test.com"
        assert data_source_user.phone == "13800138000"
        assert data_source_user.phone_country_code == "86"

        # 验证本地身份信息
        identity_info = LocalDataSourceIdentityInfo.objects.get(user=data_source_user)
        assert identity_info.data_source == data_source
        assert identity_info.username == "admin"

        # 验证管理员关联
        assert TenantManager.objects.filter(tenant=tenant, tenant_user=tenant_user).exists()

    def test_create_builtin_virtual_user(self):
        """测试创建内置虚拟用户"""
        tenant = Tenant.objects.create(id="test-tenant", name="Test Tenant")
        data_source = DataSource.objects.create(
            type=DataSourceTypeEnum.VIRTUAL,
            owner_tenant_id=tenant.id,
            plugin_id=DataSourcePluginEnum.LOCAL,
        )

        TenantCreator.create_builtin_virtual_user(
            tenant=tenant, data_source=data_source, virtual_users=[VirtualUserInfo(username="bk_admin")]
        )

        tenant_user = TenantUser.objects.filter(
            tenant=tenant, data_source=data_source, data_source_user__username="bk_admin"
        ).first()

        assert tenant_user is not None
        assert tenant_user.tenant == tenant
        assert tenant_user.data_source == data_source

        # 验证数据源用户
        data_source_user = tenant_user.data_source_user
        assert data_source_user.username == "bk_admin"
        assert data_source_user.full_name == "bk_admin"

    def test_create_builtin_idp(self):
        """测试创建内置认证源"""
        data_source = TenantCreator.create_builtin_management_data_source("test-tenant")

        idp = TenantCreator.create_builtin_idp("test-tenant", data_source.id)

        assert idp.owner_tenant_id == "test-tenant"
        assert idp.data_source_id == data_source.id
        assert idp.name == "Administrator"
