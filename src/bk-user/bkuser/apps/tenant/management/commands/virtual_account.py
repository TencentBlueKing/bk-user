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
from django.core.management import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.tenant.models import Tenant, TenantUser
from bkuser.apps.tenant.utils import TenantUserIDGenerator
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig


class Command(BaseCommand):
    """
    Virtual Account Management CLI
    $ (Query virtual accounts) python manage.py virtual_account query
    $ (Create virtual account) python manage.py virtual_account create
    $ (Update virtual account) python manage.py virtual_account update
    """

    def add_arguments(self, parser):
        """Define subcommands"""
        subparsers = parser.add_subparsers(dest="subcommand", required=True)

        # query subcommand (merged list+get)
        query_parser = subparsers.add_parser("query", help="Query virtual accounts")
        query_parser.add_argument("--tenant_id", required=True, help="Tenant ID")
        query_parser.add_argument("--login_name")
        query_parser.add_argument("--full_name")
        query_parser.add_argument("--bk_username")

        # create subcommand
        create_parser = subparsers.add_parser("create", help="Create virtual account")
        create_parser.add_argument("--tenant_id", required=True, help="Tenant ID")
        create_parser.add_argument("--login_name", required=True)
        create_parser.add_argument("--full_name", required=True)

        # update subcommand
        update_parser = subparsers.add_parser("update", help="Update virtual account")
        update_parser.add_argument("--tenant_id", required=True, help="Tenant ID")
        update_parser.add_argument("--old_login_name", required=True)
        update_parser.add_argument("--new_login_name")
        update_parser.add_argument("--new_full_name")

    @staticmethod
    def _check_tenant(tenant_id: str):
        if not Tenant.objects.filter(id=tenant_id).exists():
            raise ValueError(f"tenant {tenant_id} is not existed")

    def handle(self, *args, **options):
        subcommand = options["subcommand"]
        if subcommand not in ("query", "create", "update"):
            raise CommandError(f"subcommand {subcommand} is not supported, only support query/create/update")

        tenant_id = options["tenant_id"]
        self._check_tenant(tenant_id)
        getattr(self, f"handle_{subcommand}")(tenant_id, options)

    def handle_query(self, tenant_id: str, options):
        """Handle query virtual accounts"""
        query = Q(tenant_id=tenant_id, data_source__type=DataSourceTypeEnum.VIRTUAL)
        if login_name := options.get("login_name"):
            query &= Q(data_source_user__username=login_name)
        if full_name := options.get("full_name"):
            query &= Q(data_source_user__full_name=full_name)
        if bk_username := options.get("bk_username"):
            query &= Q(id=bk_username)

        accounts = TenantUser.objects.filter(query).select_related("data_source_user").order_by("id")

        if not accounts.exists():
            self.stdout.write("No virtual accounts found")
            return

        # Single account detail
        if any([options.get("login_name"), options.get("full_name"), options.get("bk_username")]):
            account = accounts.first()
            self.stdout.write(
                f"bk_username: {account.id}\n"
                f"login_name: {account.data_source_user.username}\n"
                f"full_name: {account.data_source_user.full_name}\n"
            )
            return

        # List all accounts
        self.stdout.write(f"Virtual accounts for tenant {tenant_id} (Total: {accounts.count()}):")
        self.stdout.write("-" * 80)
        for account in accounts:
            self.stdout.write(
                f"bk_username: {account.id}\n"
                f"login_name: {account.data_source_user.username}\n"
                f"full_name: {account.data_source_user.full_name}\n"
                f"-----------------------------"
            )

        if not accounts.exists():
            self.stdout.write("No virtual accounts found for this tenant")

    def handle_create(self, tenant_id: str, options):
        """Handle create virtual account"""
        login_name = options.get("login_name")
        full_name = options.get("full_name")

        data_source, _ = DataSource.objects.get_or_create(
            owner_tenant_id=tenant_id,
            type=DataSourceTypeEnum.VIRTUAL,
            plugin_id=DataSourcePluginEnum.LOCAL,
            defaults={"plugin_config": LocalDataSourcePluginConfig(enable_password=False)},
        )

        with transaction.atomic():
            if DataSourceUser.objects.filter(data_source=data_source, username=login_name).exists():
                raise CommandError(f"Login name '{login_name}' already exists")

            # Create data source user
            data_source_user = DataSourceUser.objects.create(
                data_source=data_source, username=login_name, full_name=full_name, code=login_name
            )

            # Create tenant user
            TenantUser.objects.create(
                id=TenantUserIDGenerator(tenant_id, data_source).gen(data_source_user),
                tenant_id=tenant_id,
                data_source_user=data_source_user,
                data_source=data_source,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created virtual account:\n" f"login_name: {login_name}\n" f"full_name: {full_name}"
            )
        )

    def handle_update(self, tenant_id: str, options):
        """Handle update virtual account"""
        old_login_name = options.get("old_login_name")
        new_login_name = options.get("new_login_name")
        new_full_name = options.get("new_full_name")

        if not old_login_name:
            raise CommandError("--login_name is required for update")
        if not any([new_login_name, new_full_name]):
            raise CommandError("At least one of --new_login_name or --new_full_name is required for update")

        with transaction.atomic():
            # Find virtual data source
            data_source = DataSource.objects.get(owner_tenant_id=tenant_id, type=DataSourceTypeEnum.VIRTUAL)

            # Find and update data source user
            try:
                user = DataSourceUser.objects.get(data_source=data_source, username=old_login_name)
                if new_login_name:
                    if (
                        DataSourceUser.objects.filter(data_source=data_source, username=new_login_name)
                        .exclude(id=user.id)
                        .exists()
                    ):
                        raise CommandError(f"New login name '{new_login_name}' already exists")
                    user.username = new_login_name

                if new_full_name:
                    user.full_name = new_full_name

                user.save()
            except DataSourceUser.DoesNotExist:
                raise CommandError(f"Virtual account with login name '{old_login_name}' not found")

        updated_fields = []
        if new_login_name:
            updated_fields.append(f"login_name: {new_login_name}")
        if new_full_name:
            updated_fields.append(f"full_name: {new_full_name}")

        self.stdout.write(self.style.SUCCESS("Successfully updated virtual account:\n" + "\n".join(updated_fields)))
