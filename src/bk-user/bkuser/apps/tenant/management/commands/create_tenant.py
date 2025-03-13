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
import re

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceUser, LocalDataSourceIdentityInfo
from bkuser.apps.idp.data_models import gen_data_source_match_rule_of_local
from bkuser.apps.idp.models import Idp
from bkuser.apps.tenant.constants import (
    DEFAULT_TENANT_USER_VALIDITY_PERIOD_CONFIG,
    TENANT_ID_REGEX,
    BuiltInTenantIDEnum,
)
from bkuser.apps.tenant.models import Tenant, TenantManager, TenantUser, TenantUserValidityPeriodConfig
from bkuser.apps.tenant.utils import TenantUserIDGenerator
from bkuser.common.constants import PERMANENT_TIME
from bkuser.common.hashers import make_password
from bkuser.common.passwd import PasswordValidator
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.idp_plugins.local.plugin import LocalIdpPluginConfig
from bkuser.plugins.base import get_default_plugin_cfg
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig


class Command(BaseCommand):
    """
    创建租户
    $ python manage.py create_tenant
    """

    def add_arguments(self, parser):
        parser.add_argument("--tenant_id", type=str, help="Tenant ID", required=True)
        parser.add_argument("--password", type=str, help="Built-In Manager - admin password", required=True)

    @staticmethod
    def _check_tenant(tenant_id: str):
        if not re.fullmatch(TENANT_ID_REGEX, tenant_id):
            raise ValueError(
                f"{tenant_id} does not meet the naming requirements for Tenant ID: must be composed of "
                "3-32 lowercase letters, digits, or hyphens (-), starting with a lowercase "
                "letter and ending with a lowercase letter or digit"
            )

        if Tenant.objects.filter(id=tenant_id).exists():
            raise ValueError(f"Tenant {tenant_id} already exists")

        if tenant_id in [BuiltInTenantIDEnum.SYSTEM, BuiltInTenantIDEnum.DEFAULT]:
            raise ValueError(f"Tenant {tenant_id} is reserved")

    @staticmethod
    def _check_password(password: str):
        cfg: LocalDataSourcePluginConfig = get_default_plugin_cfg(DataSourcePluginEnum.LOCAL)  # type: ignore
        ret = PasswordValidator(cfg.password_rule.to_rule()).validate(password)  # type: ignore
        if not ret.ok:
            raise ValueError(f"The password does not meet the password rules.:{ret.exception_message}")

    @staticmethod
    def _init_default_settings(tenant: Tenant):
        """初始化租户的默认配置"""
        # 账号有效期
        TenantUserValidityPeriodConfig.objects.create(tenant=tenant, **DEFAULT_TENANT_USER_VALIDITY_PERIOD_CONFIG)

    @staticmethod
    def _init_builtin_manager(tenant: Tenant, data_source: DataSource, password: str):
        """初始化内建管理员"""
        admin_username = "admin"
        # 创建内建管理员
        data_source_user = DataSourceUser.objects.create(
            data_source=data_source,
            code=admin_username,
            username=admin_username,
            full_name=admin_username,
        )
        LocalDataSourceIdentityInfo.objects.create(
            user=data_source_user,
            password=make_password(password),
            password_updated_at=timezone.now(),
            password_expired_at=PERMANENT_TIME,
            data_source=data_source,
            username=admin_username,
        )
        tenant_user = TenantUser.objects.create(
            tenant=tenant,
            data_source_user=data_source_user,
            data_source=data_source,
            id=TenantUserIDGenerator(tenant.id, data_source).gen(data_source_user),
        )
        TenantManager.objects.create(tenant=tenant, tenant_user=tenant_user)

    def handle(self, *args, **kwargs):
        tenant_id = kwargs["tenant_id"]
        password = kwargs["password"]

        # 校验
        self._check_tenant(tenant_id)
        self._check_password(password)

        # FIXME (nan): 目前有 GUI / Django CMD / Django Migrate 三种方式创建租户，后续需要统一复用
        #  Note: 需要注意每种方式的差异，比如 migrate 不会触发 post_save 信号、是否调用的是自定义 queryset / manager、
        #  是否支持事务、是否审计、是否发送通知等等
        with transaction.atomic():
            # 创建租户
            tenant = Tenant.objects.create(id=tenant_id, name=tenant_id)
            # 租户的一些默认配置初始化
            self._init_default_settings(tenant)

            # 创建租户内建管理的本地数据源
            data_source = DataSource.objects.create(
                type=DataSourceTypeEnum.BUILTIN_MANAGEMENT,
                owner_tenant_id=tenant.id,
                plugin_id=DataSourcePluginEnum.LOCAL,
                plugin_config=get_default_plugin_cfg(DataSourcePluginEnum.LOCAL),
            )
            # 初始化内建管理员
            self._init_builtin_manager(tenant, data_source, password)

            # 添加内置管理员账密登录认证源
            Idp.objects.create(
                name="Administrator",
                plugin_id=BuiltinIdpPluginEnum.LOCAL,
                owner_tenant_id=tenant.id,
                plugin_config=LocalIdpPluginConfig(data_source_ids=[data_source.id]),
                data_source_match_rules=[gen_data_source_match_rule_of_local(data_source.id).model_dump()],
                data_source_id=data_source.id,
            )

        # 创建租户成功提示
        self.stdout.write(
            f"create tenant [{tenant.id}] successfully, "
            "you can use admin/password to login and manage tenant organization data"
        )
