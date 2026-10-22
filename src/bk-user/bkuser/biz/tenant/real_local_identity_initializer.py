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

from django.db import transaction
from django.utils import timezone
from pydantic import BaseModel, Field, ValidationError, model_validator

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourcePlugin, DataSourceUser, LocalDataSourceIdentityInfo
from bkuser.apps.data_source.name import gen_data_source_name
from bkuser.apps.idp.constants import IdpStatus
from bkuser.apps.idp.data_models import gen_data_source_match_rule_of_local
from bkuser.apps.idp.models import Idp, IdpPlugin
from bkuser.apps.tenant.models import Tenant, TenantManager, TenantUser
from bkuser.apps.tenant.utils import TenantUserIDGenerator
from bkuser.biz.idp_data_source import IdpDataSourceRelationHandler
from bkuser.common.hashers import make_password
from bkuser.common.passwd import PasswordValidator
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.idp_plugins.local.plugin import LocalIdpPluginConfig
from bkuser.plugins.base import get_default_plugin_cfg
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.constants import USERNAME_REGEX, PasswordGenerateMethod
from bkuser.plugins.local.models import LocalDataSourcePluginConfig
from bkuser.plugins.local.utils import get_password_expired_at
from bkuser.utils.pydantic import stringify_pydantic_error


class RealLocalIdentityConfig(BaseModel):
    """实名本地身份初始化配置"""

    # 实名管理员用户名
    username: str = Field(pattern=USERNAME_REGEX.pattern)
    # 实名管理员密码
    password: str
    # 该数据源后续新增用户的初始密码生成方式，与管理员密码无关
    new_user_password_method: PasswordGenerateMethod = PasswordGenerateMethod.RANDOM
    # 后续新增用户的固定初始密码，仅生成方式为固定值时有效
    new_user_fixed_password: str = ""

    @model_validator(mode="after")
    def validate_passwords(self) -> "RealLocalIdentityConfig":
        # 此处只校验参数间约束，不校验密码强度；密码强度由 RealLocalIdentityInitializer 按实际数据源配置校验
        if not self.password:
            raise ValueError("password is required")

        if self.new_user_password_method == PasswordGenerateMethod.FIXED:
            if not self.new_user_fixed_password:
                raise ValueError("new_user_fixed_password is required when new_user_password_method is fixed")
        elif self.new_user_fixed_password:
            raise ValueError("new_user_fixed_password is only allowed when new_user_password_method is fixed")

        return self


class RealLocalIdentityInitError(RuntimeError):
    """实名本地身份初始化失败"""


class RealLocalIdentityInitializer:
    """为租户初始化实名本地身份：实名本地数据源、账密登录认证源及实名管理员"""

    def __init__(self, tenant_id: str, config: RealLocalIdentityConfig):
        self.tenant_id = tenant_id
        self.config = config

    @transaction.atomic
    def initialize(self) -> bool:
        """初始化租户，返回是否有新创建数据。

        已有实名本地数据源，或已有本地账密登录认证源时跳过。
        """
        plugin_config = self._build_local_plugin_config()

        tenant = Tenant.objects.filter(id=self.tenant_id).first()
        if tenant is None:
            raise RealLocalIdentityInitError(f"tenant [{self.tenant_id}] does not exist")

        # 实名本地数据源还在，说明已经初始化过或在页面上配置过，不再重复创建
        if DataSource.objects.filter(
            owner_tenant_id=tenant.id,
            type=DataSourceTypeEnum.REAL,
            plugin_id=DataSourcePluginEnum.LOCAL,
        ).exists():
            return False

        # 数据源已经不在，但本地实名认证源还留着，说明是在页面上删掉的，不再补建
        if IdpDataSourceRelationHandler.has_duplicate_plugin_real_relation(tenant.id, BuiltinIdpPluginEnum.LOCAL):
            return False

        data_source = self._create_local_data_source(tenant, plugin_config)
        self._create_local_idp(tenant, data_source)
        tenant_user = self._create_tenant_user(tenant, data_source)
        TenantManager.objects.create(tenant=tenant, tenant_user=tenant_user)
        return True

    def _build_local_plugin_config(self) -> LocalDataSourcePluginConfig:
        """构建实名本地数据源的插件配置，并按其密码规则校验管理员密码"""
        # 除启用账密登录及新增用户的初始密码外，其余配置与页面新建本地数据源时的默认配置保持一致
        cfg = get_default_plugin_cfg(DataSourcePluginEnum.LOCAL).model_dump()
        cfg["enable_password"] = True
        if self.config.new_user_password_method == PasswordGenerateMethod.FIXED:
            cfg["password_initial"]["generate_method"] = PasswordGenerateMethod.FIXED
            cfg["password_initial"]["fixed_password"] = self.config.new_user_fixed_password

        # LocalDataSourcePluginConfig 未开启赋值校验，需通过构建触发固定密码强度等校验
        try:
            plugin_config = LocalDataSourcePluginConfig.model_validate(cfg)
        except ValidationError as e:
            raise RealLocalIdentityInitError(f"invalid local data source plugin config: {stringify_pydantic_error(e)}")

        assert plugin_config.password_rule is not None
        ret = PasswordValidator(plugin_config.password_rule.to_rule()).validate(self.config.password)
        if not ret.ok:
            raise RealLocalIdentityInitError(f"password does not satisfy the password rules: {ret.exception_message}")

        return plugin_config

    def _create_local_data_source(self, tenant: Tenant, plugin_config: LocalDataSourcePluginConfig) -> DataSource:
        plugin = DataSourcePlugin.objects.get(id=DataSourcePluginEnum.LOCAL)
        return DataSource.objects.create(
            owner_tenant_id=tenant.id,
            name=gen_data_source_name(DataSourceTypeEnum.REAL, plugin.name),
            type=DataSourceTypeEnum.REAL,
            plugin=plugin,
            plugin_config=plugin_config,
        )

    def _create_local_idp(self, tenant: Tenant, data_source: DataSource) -> Idp:
        plugin = IdpPlugin.objects.get(id=BuiltinIdpPluginEnum.LOCAL)
        idp = Idp.objects.create(
            owner_tenant_id=tenant.id,
            name=plugin.name,
            status=IdpStatus.ENABLED,
            plugin=plugin,
            plugin_config=LocalIdpPluginConfig(),
        )

        IdpDataSourceRelationHandler.set_real_relations_from_match_rules(
            idp,
            [gen_data_source_match_rule_of_local(data_source.id)],
        )
        return idp

    def _create_tenant_user(self, tenant: Tenant, data_source: DataSource) -> TenantUser:
        """仅为当前租户创建实名管理员，不处理页面创建用户的扩展流程：

        - 不转换用户名，不关联部门、上级及协同租户
        - 使用指定密码直接初始化身份，不应用新用户初始密码策略，也不发送通知
        """
        data_source_user = DataSourceUser.objects.create(
            data_source=data_source,
            code=self.config.username,
            username=self.config.username,
            full_name=self.config.username,
        )
        tenant_user = TenantUser.objects.create(
            id=TenantUserIDGenerator(tenant.id, data_source).gen(data_source_user),
            tenant=tenant,
            data_source=data_source,
            data_source_user=data_source_user,
        )

        # 管理员密码不走数据源的初始密码策略，但过期时间仍按数据源的密码有效期计算
        plugin_config = data_source.get_plugin_cfg()
        assert isinstance(plugin_config, LocalDataSourcePluginConfig)
        assert plugin_config.password_expire is not None
        LocalDataSourceIdentityInfo.objects.create(
            user=data_source_user,
            password=make_password(self.config.password),
            password_updated_at=timezone.now(),
            password_expired_at=get_password_expired_at(plugin_config.password_expire.valid_time),
            data_source=data_source,
            username=data_source_user.username,
        )
        return tenant_user
