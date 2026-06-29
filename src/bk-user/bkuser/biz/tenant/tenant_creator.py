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

from typing import List, Optional

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from pydantic import BaseModel, Field

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceUser,
    DataSourceUsernameGenerateConfig,
    LocalDataSourceIdentityInfo,
)
from bkuser.apps.idp.models import Idp
from bkuser.apps.tenant.constants import (
    DEFAULT_TENANT_USER_DISPLAY_NAME_EXPRESSION_CONFIG,
    DEFAULT_TENANT_USER_VALIDITY_PERIOD_CONFIG,
    TenantStatus,
)
from bkuser.apps.tenant.models import (
    Tenant,
    TenantManager,
    TenantUser,
    TenantUserDisplayNameExpressionConfig,
    TenantUserValidityPeriodConfig,
)
from bkuser.apps.tenant.utils import TenantUserIDGenerator
from bkuser.biz.idp_data_source import IdpDataSourceRelationHandler
from bkuser.common.constants import PERMANENT_TIME
from bkuser.common.hashers import make_password
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.idp_plugins.local.plugin import LocalIdpPluginConfig
from bkuser.plugins.base import get_default_plugin_cfg
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.constants import NEVER_EXPIRE_TIME, NotificationMethod, PasswordGenerateMethod
from bkuser.plugins.local.models import LocalDataSourcePluginConfig
from bkuser.settings import DEFAULT_TENANT_LOGO


class TenantInfo(BaseModel):
    """租户基础信息配置"""

    tenant_id: str
    tenant_name: str
    logo: str = DEFAULT_TENANT_LOGO
    status: TenantStatus = TenantStatus.ENABLED
    is_default: bool = False


class BuiltinManagerInfo(BaseModel):
    """内置管理员配置"""

    username: str = "admin"
    password: str = ""
    email: str = ""
    phone: str = ""
    phone_country_code: str = settings.DEFAULT_PHONE_COUNTRY_CODE


class BuiltinManagementDataSourceConfig(BaseModel):
    """内置管理数据源配置"""

    send_password_notification: bool = True
    fixed_password: str = ""
    notification_methods: List[str] = Field(default_factory=list)


class VirtualUserInfo(BaseModel):
    """虚拟用户信息"""

    username: str = "bk_admin"

    # [非多租户] 兼容 2.x 版本 对于 admin 的内置用户特殊处理，支持指定 tenant_user_id
    tenant_user_id: str = ""


class TenantCreator:
    @staticmethod
    def create_tenant_base(info: TenantInfo) -> Tenant:
        """创建租户基础信息"""
        tenant, _ = Tenant.objects.get_or_create(
            id=info.tenant_id,
            defaults={
                "name": info.tenant_name,
                "logo": info.logo,
                "status": info.status,
                "is_default": info.is_default,
            },
        )
        return tenant

    @staticmethod
    def create_tenant_default_settings(tenant: Tenant) -> None:
        """创建租户默认配置"""
        # 账号有效期
        TenantUserValidityPeriodConfig.objects.get_or_create(
            tenant=tenant,
            defaults=DEFAULT_TENANT_USER_VALIDITY_PERIOD_CONFIG,
        )
        # DisplayName 表达式
        TenantUserDisplayNameExpressionConfig.objects.get_or_create(
            tenant=tenant, defaults=DEFAULT_TENANT_USER_DISPLAY_NAME_EXPRESSION_CONFIG
        )

    @staticmethod
    def create_builtin_management_data_source(
        tenant_id: str,
        enable_password: bool = True,
        fixed_password: str = "",
        notification_methods: Optional[List[str]] = None,
    ) -> DataSource:
        """创建内置管理数据源

        :param tenant_id: 租户 ID
        :param enable_password: 是否启用密码功能
        :param fixed_password: 固定密码
        :param notification_methods: 通知方式列表
        """
        # 获取本地数据源的默认配置
        plugin_id = DataSourcePluginEnum.LOCAL
        plugin_config = get_default_plugin_cfg(plugin_id)
        assert isinstance(plugin_config, LocalDataSourcePluginConfig)
        assert plugin_config.password_initial is not None
        assert plugin_config.login_limit is not None
        assert plugin_config.password_expire is not None

        # 根据参数配置插件
        if enable_password:
            plugin_config.enable_password = True
            plugin_config.password_expire.valid_time = NEVER_EXPIRE_TIME

            if fixed_password:
                plugin_config.password_initial.generate_method = PasswordGenerateMethod.FIXED
                plugin_config.password_initial.fixed_password = fixed_password

            if notification_methods:
                plugin_config.password_initial.notification.enabled_methods = [
                    NotificationMethod(n) for n in notification_methods
                ]

        ds, _ = DataSource.objects.get_or_create(
            type=DataSourceTypeEnum.BUILTIN_MANAGEMENT,
            owner_tenant_id=tenant_id,
            defaults={
                "plugin_id": plugin_id,
                "plugin_config": plugin_config,
            },
        )
        DataSourceUsernameGenerateConfig.objects.get_or_create(data_source=ds)
        return ds

    @staticmethod
    def create_virtual_data_source(tenant_id: str) -> DataSource:
        """创建虚拟数据源"""
        ds, _ = DataSource.objects.get_or_create(
            owner_tenant_id=tenant_id,
            type=DataSourceTypeEnum.VIRTUAL,
            defaults={
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": LocalDataSourcePluginConfig(enable_password=False),
            },
        )
        DataSourceUsernameGenerateConfig.objects.get_or_create(data_source=ds)
        return ds

    @staticmethod
    def create_builtin_manager(
        tenant: Tenant,
        data_source: DataSource,
        built_manager: BuiltinManagerInfo,
    ) -> TenantUser:
        """创建内置管理员"""
        # 创建数据源用户
        data_source_user, created = DataSourceUser.objects.get_or_create(
            data_source=data_source,
            username=built_manager.username,
            defaults={
                "code": built_manager.username,
                "full_name": built_manager.username,
                "email": built_manager.email,
                "phone": built_manager.phone,
                "phone_country_code": built_manager.phone_country_code,
            },
        )

        # 创建本地身份信息
        if built_manager.password and created:
            LocalDataSourceIdentityInfo.objects.create(
                user=data_source_user,
                password=make_password(built_manager.password),
                password_updated_at=timezone.now(),
                password_expired_at=PERMANENT_TIME,
                data_source=data_source,
                username=built_manager.username,
            )

        # 创建租户用户
        tenant_user, _ = TenantUser.objects.get_or_create(
            tenant=tenant,
            data_source_user=data_source_user,
            data_source=data_source,
            defaults={"id": TenantUserIDGenerator(tenant.id, data_source).gen(data_source_user)},
        )

        # 创建管理员关联
        TenantManager.objects.get_or_create(tenant=tenant, tenant_user=tenant_user)

        return tenant_user

    @staticmethod
    def create_builtin_virtual_user(tenant: Tenant, data_source: DataSource, virtual_users: List[VirtualUserInfo]):
        """创建内置虚拟用户"""
        # 内置虚拟用户并不会很多，这里就不考虑批量创建
        for vuser in virtual_users:
            data_source_user, _ = DataSourceUser.objects.get_or_create(
                data_source=data_source,
                username=vuser.username,
                defaults={"full_name": vuser.username, "code": vuser.username},
            )

            # 若未指定 tenant_user_id，则自动生成
            tenant_user_id = (
                TenantUserIDGenerator(tenant.id, data_source).gen(data_source_user)
                if not vuser.tenant_user_id
                else vuser.tenant_user_id
            )

            TenantUser.objects.get_or_create(
                tenant_id=tenant.id,
                data_source_user=data_source_user,
                defaults={"data_source": data_source, "id": tenant_user_id},
            )

    @staticmethod
    def create_builtin_idp(tenant_id: str, data_source_id: int, name: str = "Administrator") -> Idp:
        """创建内置管理员账密登录认证源"""
        data_source = DataSource.objects.get(id=data_source_id)
        idp, _ = Idp.objects.get_or_create(
            plugin_id=BuiltinIdpPluginEnum.LOCAL,
            owner_tenant_id=tenant_id,
            name=name,
            defaults={
                "plugin_config": LocalIdpPluginConfig(data_source_ids=[data_source_id]),
            },
        )
        IdpDataSourceRelationHandler.set_builtin_management_relation(idp, data_source)
        return idp

    @staticmethod
    def create(
        tenant_info: TenantInfo,
        builtin_manager: BuiltinManagerInfo,
        builtin_ds_config: BuiltinManagementDataSourceConfig,
        virtual_users: List[VirtualUserInfo] | None = None,
    ) -> Tenant:
        """创建租户的统一入口方法

        :param tenant_info: 租户相关信息
        :param builtin_manager: 内置管理员信息
        :param builtin_ds_config: 内置数据源配置
        :param virtual_users: 虚拟用户相关信息列表
        :return: 创建的租户对象
        """

        # 注意：校验应由上层完成；此处仅负责创建流程

        with transaction.atomic():
            # 阶段 1：创建租户基础信息
            tenant = TenantCreator.create_tenant_base(tenant_info)

            # 阶段 2：初始化租户默认配置
            TenantCreator.create_tenant_default_settings(tenant)

            # 阶段 3：创建内置管理数据源
            data_source = TenantCreator.create_builtin_management_data_source(
                tenant.id,
                enable_password=True,
                fixed_password=builtin_ds_config.fixed_password,
                notification_methods=(
                    builtin_ds_config.notification_methods if builtin_ds_config.send_password_notification else None
                ),
            )

            # 阶段 4：创建内置管理员
            TenantCreator.create_builtin_manager(
                tenant=tenant,
                data_source=data_source,
                built_manager=builtin_manager,
            )

            # 阶段 5：创建虚拟数据源
            virtual_data_source = TenantCreator.create_virtual_data_source(tenant.id)

            # 阶段 6：创建内置虚拟用户
            if virtual_users:
                TenantCreator.create_builtin_virtual_user(tenant, virtual_data_source, virtual_users)

            # 阶段 7：创建内置认证源
            TenantCreator.create_builtin_idp(tenant.id, data_source.id)

        return tenant
