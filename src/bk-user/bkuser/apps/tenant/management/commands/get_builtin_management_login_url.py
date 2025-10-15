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
from django.core.management.base import BaseCommand

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.idp.models import Idp
from bkuser.apps.tenant.constants import BuiltInTenantIDEnum
from bkuser.apps.tenant.models import Tenant
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.utils.url import urljoin


class Command(BaseCommand):
    """获取内置管理员登录地址"""

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

    def handle(self, *args, **options):
        tenant_id = options.get("tenant_id")
        self._check_tenant_id(tenant_id)

        # 非多租户模式：始终使用 DEFAULT
        if not settings.ENABLE_MULTI_TENANT_MODE:
            tenant_id = BuiltInTenantIDEnum.DEFAULT

        data_source = DataSource.objects.get(
            owner_tenant_id=tenant_id,
            type=DataSourceTypeEnum.BUILTIN_MANAGEMENT,
        )

        idp = Idp.objects.get(
            owner_tenant_id=tenant_id,
            plugin_id=BuiltinIdpPluginEnum.LOCAL,
            data_source_id=data_source.id,
        )

        login_url = urljoin(settings.BK_LOGIN_URL, f"/builtin-management-auth/idps/{idp.id}/")

        self.stdout.write(login_url)
