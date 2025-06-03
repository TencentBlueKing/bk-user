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
import json

from django.core.management import BaseCommand, CommandError
from django.db import transaction

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.tenant.models import Tenant, TenantUser
from bkuser.apps.tenant.utils import TenantUserIDGenerator
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig


class Command(BaseCommand):
    """
    Virtual User Management CLI
    $ (Get virtual user) python manage.py virtual_user get
    $ (Upsert virtual user) python manage.py virtual_user upsert
    """

    def add_arguments(self, parser):
        """Define subcommands"""
        subparsers = parser.add_subparsers(dest="subcommand", required=True)

        # get subcommand
        get_parser = subparsers.add_parser("get", help="Get virtual users")
        get_parser.add_argument("--tenant_id", required=True, help="Tenant ID")
        get_parser.add_argument("--username", required=True)

        # upsert subcommand
        upsert_parser = subparsers.add_parser("upsert", help="Upsert virtual user")
        upsert_parser.add_argument("--tenant_id", required=True, help="Tenant ID")
        upsert_parser.add_argument("--username", required=True)
        upsert_parser.add_argument("--full_name", required=True)

    @staticmethod
    def _check_tenant(tenant_id: str):
        if not Tenant.objects.filter(id=tenant_id).exists():
            raise ValueError(f"tenant {tenant_id} is not existed")

    def handle(self, *args, **options):
        subcommand = options["subcommand"]
        if subcommand not in ("get", "upsert"):
            raise CommandError(f"subcommand {subcommand} is not supported, only support get/upsert")

        tenant_id = options["tenant_id"]
        self._check_tenant(tenant_id)
        getattr(self, f"handle_{subcommand}")(tenant_id, options)

    def handle_get(self, tenant_id: str, options):
        """Handle get virtual user"""

        user = (
            TenantUser.objects.select_related("data_source_user")
            .filter(
                tenant_id=tenant_id,
                data_source__type=DataSourceTypeEnum.VIRTUAL,
                data_source_user__username=options["username"],
            )
            .first()
        )

        if not user:
            raise ValueError(f"Virtual user with username '{options['username']}' not found")

        self.stdout.write(
            json.dumps(
                {
                    "tenant_user_id": user.id,
                    "username": user.data_source_user.username,
                    "full_name": user.data_source_user.full_name,
                },
                ensure_ascii=False,
            )
        )

    def handle_upsert(self, tenant_id: str, options):
        """upsert virtual user"""
        username = options["username"]
        full_name = options["full_name"]

        data_source, _ = DataSource.objects.get_or_create(
            owner_tenant_id=tenant_id,
            type=DataSourceTypeEnum.VIRTUAL,
            defaults={
                "plugin_config": LocalDataSourcePluginConfig(enable_password=False),
                "plugin_id": DataSourcePluginEnum.LOCAL,
            },
        )

        with transaction.atomic():
            # Update if already exists
            data_source_user, created = DataSourceUser.objects.update_or_create(
                data_source=data_source,
                username=username,
                defaults={
                    "full_name": full_name,
                    "code": username,
                },
            )

            if created:
                # Create tenant user only for newly created data source user
                TenantUser.objects.create(
                    id=TenantUserIDGenerator(tenant_id, data_source).gen(data_source_user),
                    tenant_id=tenant_id,
                    data_source_user=data_source_user,
                    data_source=data_source,
                )

        self.stdout.write(f"Successfully upserted virtual user: {username}")
