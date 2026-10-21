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

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from pydantic import ValidationError

from bkuser.apps.tenant.constants import BuiltInTenantIDEnum
from bkuser.biz.tenant import RealLocalIdentityConfig, RealLocalIdentityInitError, RealLocalIdentityInitializer
from bkuser.plugins.local.constants import PasswordGenerateMethod
from bkuser.utils.pydantic import stringify_pydantic_error


class Command(BaseCommand):
    """
    为租户初始化实名本地身份：实名本地数据源、账密登录认证源及实名管理员，已初始化过则跳过
    $ python manage.py init_real_local_identity
    """

    help = "Initialize real local data source, local password login and a real manager for the tenant"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tenant_id",
            type=str,
            help="Tenant ID (required in multi-tenant mode, ignored in single-tenant mode)",
        )
        parser.add_argument("--username", type=str, required=True, help="Real manager username")
        parser.add_argument("--password", type=str, required=True, help="Real manager password")
        parser.add_argument(
            "--new_user_password_method",
            type=str,
            choices=[PasswordGenerateMethod.RANDOM.value, PasswordGenerateMethod.FIXED.value],
            default=PasswordGenerateMethod.RANDOM.value,
            help="Initial password method for users added to the data source later",
        )
        parser.add_argument(
            "--new_user_fixed_password",
            type=str,
            default="",
            help="Fixed initial password for users added later (required when the method is fixed)",
        )

    def _get_tenant_id(self, tenant_id: str | None) -> str:
        if not settings.ENABLE_MULTI_TENANT_MODE:
            if tenant_id and tenant_id != BuiltInTenantIDEnum.DEFAULT:
                self.stderr.write(f"tenant_id [{tenant_id}] is ignored in single-tenant mode, use default tenant")
            return BuiltInTenantIDEnum.DEFAULT

        if not tenant_id:
            raise CommandError("the tenant_id is required when multi-tenant mode enabled")
        return tenant_id

    def handle(self, *args, **options):
        tenant_id = self._get_tenant_id(options.get("tenant_id"))

        try:
            config = RealLocalIdentityConfig(
                username=options["username"],
                password=options["password"],
                new_user_password_method=options["new_user_password_method"],
                new_user_fixed_password=options["new_user_fixed_password"],
            )
        except ValidationError as e:
            raise CommandError(f"invalid arguments: {stringify_pydantic_error(e)}")

        try:
            created = RealLocalIdentityInitializer(tenant_id, config).initialize()
        except RealLocalIdentityInitError as e:
            raise CommandError(f"failed to initialize real local identity: {e}")

        if created:
            self.stdout.write(f"tenant [{tenant_id}] real local identity initialized successfully")
        else:
            self.stdout.write(f"tenant [{tenant_id}] already has real local identity configured, skip...")
