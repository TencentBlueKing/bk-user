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

import datetime

from django.db import transaction
from django.utils import timezone
from pydantic import BaseModel, Field, model_validator

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourcePlugin, DataSourceUser, LocalDataSourceIdentityInfo
from bkuser.apps.data_source.name import gen_data_source_name
from bkuser.apps.idp.constants import IdpStatus
from bkuser.apps.idp.data_models import gen_data_source_match_rule_of_local
from bkuser.apps.idp.models import Idp, IdpPlugin
from bkuser.apps.tenant.models import Tenant, TenantManager, TenantUser
from bkuser.apps.tenant.utils import TenantUserIDGenerator
from bkuser.biz.idp_data_source import IdpDataSourceRelationHandler
from bkuser.common.constants import PERMANENT_TIME
from bkuser.common.hashers import make_password
from bkuser.common.passwd import PasswordValidator
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.idp_plugins.local.plugin import LocalIdpPluginConfig
from bkuser.plugins.base import get_default_plugin_cfg
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.constants import USERNAME_REGEX, PasswordGenerateMethod
from bkuser.plugins.local.models import LocalDataSourcePluginConfig


def _get_default_local_plugin_config() -> LocalDataSourcePluginConfig:
    plugin_config = get_default_plugin_cfg(DataSourcePluginEnum.LOCAL)
    assert isinstance(plugin_config, LocalDataSourcePluginConfig)
    return plugin_config


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
        plugin_config = _get_default_local_plugin_config()
        assert plugin_config.password_rule is not None
        validator = PasswordValidator(plugin_config.password_rule.to_rule())

        # 空字符串会让密码强度校验直接报错，需先单独拦截
        if not self.password:
            raise ValueError("password is required")
        if not (ret := validator.validate(self.password)).ok:
            raise ValueError(f"password does not satisfy the password rules: {ret.exception_message}")

        if self.new_user_password_method == PasswordGenerateMethod.FIXED:
            if not self.new_user_fixed_password:
                raise ValueError("new_user_fixed_password is required when new_user_password_method is fixed")
            if not (ret := validator.validate(self.new_user_fixed_password)).ok:
                raise ValueError(
                    f"new_user_fixed_password does not satisfy the password rules: {ret.exception_message}"
                )
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

        已有实名本地数据源，或已有本地实名认证源时跳过。
        """
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

        data_source = self._create_local_data_source(tenant)
        self._create_local_idp(tenant, data_source)
        tenant_user = self._create_tenant_user(tenant, data_source)
        TenantManager.objects.create(tenant=tenant, tenant_user=tenant_user)
        return True

    def _create_local_data_source(self, tenant: Tenant) -> DataSource:
        plugin_config = _get_default_local_plugin_config()

        # 除启用账密登录及新增用户的初始密码外，其余配置与页面新建本地数据源时的默认配置保持一致
        plugin_config.enable_password = True
        if self.config.new_user_password_method == PasswordGenerateMethod.FIXED:
            assert plugin_config.password_initial is not None
            plugin_config.password_initial.generate_method = PasswordGenerateMethod.FIXED
            plugin_config.password_initial.fixed_password = self.config.new_user_fixed_password

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
        now = timezone.now()
        valid_time = plugin_config.password_expire.valid_time
        LocalDataSourceIdentityInfo.objects.create(
            user=data_source_user,
            password=make_password(self.config.password),
            password_updated_at=now,
            password_expired_at=PERMANENT_TIME if valid_time < 0 else now + datetime.timedelta(days=valid_time),
            data_source=data_source,
            username=data_source_user.username,
        )
        return tenant_user
