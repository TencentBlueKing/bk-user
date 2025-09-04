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

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.idp.models import Idp
from bkuser.apps.tenant.constants import BuiltInTenantIDEnum
from bkuser.apps.tenant.models import Tenant
from bkuser.biz.tenant import BuiltinManagementLoginUrlTokenManager
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.utils.url import urljoin


class Command(BaseCommand):
    """
    内置管理员登录地址
    $（生成内置管理员登录地址）python manage.py builtin_management_login_url generate
    $（获取内置管理员登录地址）python manage.py builtin_management_login_url get
    """

    def add_arguments(self, parser):
        # 定义子命令
        subparsers = parser.add_subparsers(dest="subcommand", required=True)

        # generate 子命令
        generate_parser = subparsers.add_parser("generate", help="Generate builtin management login URL")
        generate_parser.add_argument("--tenant_id", type=str, help="Tenant ID")
        generate_parser.add_argument(
            "--valid_time",
            type=int,
            help="Token valid time in days",
            default=settings.DEFAULT_BUILTIN_MANAGEMENT_LOGIN_URL_VALID_TIME,
        )

        # get 子命令
        get_parser = subparsers.add_parser("get", help="Get builtin management login URL")
        get_parser.add_argument("--tenant_id", type=str, help="Tenant ID")

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

    def handle(self, *args, **options):
        # 子命令校验
        subcommand = options["subcommand"]
        if subcommand not in ("generate", "get"):
            raise CommandError(f"subcommand {options['subcommand']} is not supported, only support generate/get")

        # 公共参数
        tenant_id = options["tenant_id"]
        # 校验
        self._check_tenant_id(tenant_id)

        # 非多租户模式：始终使用 DEFAULT
        if not settings.ENABLE_MULTI_TENANT_MODE:
            tenant_id = BuiltInTenantIDEnum.DEFAULT

        # 获取数据源和认证源
        data_source = DataSource.objects.get(
            owner_tenant_id=tenant_id,
            type=DataSourceTypeEnum.BUILTIN_MANAGEMENT,
        )

        idp = Idp.objects.get(
            owner_tenant_id=tenant_id,
            plugin_id=BuiltinIdpPluginEnum.LOCAL,
            data_source_id=data_source.id,
        )

        # 子命令处理
        getattr(self, f"handle_{subcommand}")(idp, options)

    def handle_generate(self, idp: Idp, options: dict):
        valid_time = options["valid_time"]

        # 将有效时间转换为秒
        expires_in = valid_time * 3600 * 24

        # 生成 token
        token_manager = BuiltinManagementLoginUrlTokenManager()
        token = token_manager.generate_login_url_token(idp.id, expires_in)

        # 构建登录 URL
        login_url = urljoin(settings.BK_LOGIN_URL, f"/builtin-management-auth/{token}/idps/{idp.id}/")
        self.stdout.write(f"登录地址为: {login_url}, 过期时间为 {valid_time} 天")

    def handle_get(self, idp: Idp, options: dict):
        # 生成 token 并构建完整的登录 URL
        token_manager = BuiltinManagementLoginUrlTokenManager()
        token = token_manager.get_login_url_token(idp.id)

        if not token:
            self.stdout.write("登录地址无效或已过期，请重新生成")
            return

        login_url = urljoin(settings.BK_LOGIN_URL, f"/builtin-management-auth/{token}/idps/{idp.id}/")

        self.stdout.write(login_url)
