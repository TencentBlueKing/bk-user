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

import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceUser,
    DataSourceUserDeprecatedPasswordRecord,
    LocalDataSourceIdentityInfo,
)
from bkuser.apps.tenant.constants import BuiltInTenantIDEnum
from bkuser.apps.tenant.models import Tenant
from bkuser.common.hashers import make_password
from bkuser.common.passwd.generator import PasswordGenerator
from bkuser.plugins.base import get_default_plugin_cfg
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig


class Command(BaseCommand):
    """
    更新内置管理员密码
    $ python manage.py update_builtin_management_password
    """

    def add_arguments(self, parser):
        parser.add_argument("--tenant_id", type=str, help="Tenant ID (required in multi-tenant mode)")

    @staticmethod
    def _check_tenant_id(tenant_id: str | None):
        # 非多租户，无需校验，因为即使传入了，也不会使用到
        if not settings.ENABLE_MULTI_TENANT_MODE:
            return

        # 多租户模式：必须提供 tenant_id
        if not tenant_id:
            raise ValueError("the tenant_id is required when multi-tenant mode enabled")

        # 检查租户是否存在
        if not Tenant.objects.filter(id=tenant_id).exists():
            raise ValueError(f"tenant {tenant_id} is not existed")

    @staticmethod
    def _generate_password():
        cfg: LocalDataSourcePluginConfig = get_default_plugin_cfg(DataSourcePluginEnum.LOCAL)  # type: ignore
        return PasswordGenerator(cfg.password_rule.to_rule()).generate()  # type: ignore

    @staticmethod
    def _update_password(
        data_source_user: DataSourceUser,
        password: str,
        valid_days: int,
        operator: str,
    ):
        """
        更新密码
        """
        identify_info = LocalDataSourceIdentityInfo.objects.get(user=data_source_user)
        deprecated_password = identify_info.password

        with transaction.atomic():
            identify_info.password = make_password(password)
            identify_info.password_updated_at = timezone.now()
            identify_info.password_expired_at = timezone.now() + datetime.timedelta(days=valid_days)

            identify_info.save(update_fields=["password", "password_updated_at", "password_expired_at", "updated_at"])

            DataSourceUserDeprecatedPasswordRecord.objects.create(
                user=data_source_user, password=deprecated_password, operator=operator
            )

    def handle(self, *args, **options):
        tenant_id = options.get("tenant_id")
        self._check_tenant_id(tenant_id)

        # 非多租户模式：始终使用 DEFAULT
        if not settings.ENABLE_MULTI_TENANT_MODE:
            tenant_id = BuiltInTenantIDEnum.DEFAULT

        # 获取数据源和认证源
        data_source = DataSource.objects.get(
            owner_tenant_id=tenant_id,
            type=DataSourceTypeEnum.BUILTIN_MANAGEMENT,
        )

        data_source_user = DataSourceUser.objects.get(
            data_source=data_source,
            username="admin",
        )

        raw_password = self._generate_password()

        valid_time = data_source.get_plugin_cfg().password_expire.valid_time

        self._update_password(
            data_source_user=data_source_user,
            password=raw_password,
            valid_days=valid_time,
            operator="ops",
        )

        self.stdout.write(
            f"Generated builtin management password: {raw_password}, password valid time is {valid_time} days"
        )
