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

from bkuser.apps.tenant.constants import TENANT_ID_REGEX, BuiltInTenantIDEnum
from bkuser.apps.tenant.models import Tenant
from bkuser.biz.tenant import (
    BuiltinManagementDataSourceConfig,
    BuiltinManagerInfo,
    TenantCreator,
    TenantInfo,
)
from bkuser.common.passwd.generator import PasswordGenerator
from bkuser.plugins.base import get_default_plugin_cfg
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.constants import BUILTIN_MANAGEMENT_PASSWORD_VALID_TIME, MAX_PASSWORD_VALID_TIME
from bkuser.plugins.local.models import LocalDataSourcePluginConfig


class Command(BaseCommand):
    """
    创建租户
    $ python manage.py create_tenant
    """

    def add_arguments(self, parser):
        parser.add_argument("--tenant_id", type=str, help="Tenant ID", required=True)
        parser.add_argument(
            "--password_valid_time",
            type=int,
            help="Password valid time",
            default=BUILTIN_MANAGEMENT_PASSWORD_VALID_TIME,
        )

    @staticmethod
    def _check_tenant(tenant_id: str):
        if not re.fullmatch(TENANT_ID_REGEX, tenant_id):
            raise ValueError(
                f"{tenant_id} does not meet the naming requirements for Tenant ID: must be composed of "
                "3-32 lowercase letters, digits, or hyphens (-), starting with a lowercase "
                "letter and ending with a lowercase letter or digit, and cannot contain two consecutive hyphens(--)"
            )

        if Tenant.objects.filter(id=tenant_id).exists():
            raise ValueError(f"Tenant {tenant_id} already exists")

        if tenant_id in [BuiltInTenantIDEnum.SYSTEM, BuiltInTenantIDEnum.DEFAULT]:
            raise ValueError(f"Tenant {tenant_id} is reserved")

    @staticmethod
    def _check_password_valid_time(password_valid_time: int):
        if password_valid_time <= 0:
            raise ValueError("Password valid time must be greater than 0")

        if password_valid_time > MAX_PASSWORD_VALID_TIME:
            raise ValueError("Password valid time must be less than 10 years")

    @staticmethod
    def _generate_password():
        cfg: LocalDataSourcePluginConfig = get_default_plugin_cfg(DataSourcePluginEnum.LOCAL)  # type: ignore
        return PasswordGenerator(cfg.password_rule.to_rule()).generate()  # type: ignore

    def handle(self, *args, **kwargs):
        tenant_id = kwargs["tenant_id"]
        password_valid_time = kwargs["password_valid_time"]

        # 校验
        self._check_tenant(tenant_id)
        self._check_password_valid_time(password_valid_time)
        # 随机生成密码
        password = self._generate_password()

        # 创建租户
        tenant = TenantCreator.create(
            tenant_info=TenantInfo(tenant_id=tenant_id, tenant_name=tenant_id, is_default=False),
            builtin_manager=BuiltinManagerInfo(
                username="admin", password=password, password_valid_time=password_valid_time
            ),
            builtin_ds_config=BuiltinManagementDataSourceConfig(send_password_notification=False),
        )

        # 创建租户成功提示
        self.stdout.write(
            f"create tenant [{tenant.id}] successfully, "
            "you can use admin/password to login and manage tenant organization data"
        )
