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

from bkuser.apps.tenant.models import Tenant, TenantCommonVariable


class Command(BaseCommand):
    """
    租户公共变量统一管理 CLI
    $（列出所有公共变量）python manage.py tenant_common_variable list
    $（获取公共变量）python manage.py tenant_common_variable get
    $（变更公共变量）python manage.py tenant_common_variable upsert
    $（删除公共变量）python manage.py tenant_common_variable delete
    """

    def add_arguments(self, parser):
        # 定义子命令
        subparsers = parser.add_subparsers(dest="subcommand", required=True)

        # list 子命令
        list_parser = subparsers.add_parser("list", help="List all tenant common variables")
        list_parser.add_argument("--tenant_id", type=str, help="Tenant ID", required=True)

        # get 子命令
        get_parser = subparsers.add_parser("get", help="Get tenant common variable")
        get_parser.add_argument("--tenant_id", type=str, help="Tenant ID", required=True)
        get_parser.add_argument("--name", type=str, help="Name of the tenant common variable", required=True)

        # delete 子命令
        delete_parser = subparsers.add_parser("delete", help="Delete tenant common variable")
        delete_parser.add_argument("--tenant_id", type=str, help="Tenant ID", required=True)
        delete_parser.add_argument("--name", type=str, help="Name of the tenant common variable", required=True)

        # upsert 子命令
        upsert_parser = subparsers.add_parser("upsert", help="Upsert tenant common variable")
        upsert_parser.add_argument("--tenant_id", type=str, help="Tenant ID", required=True)
        upsert_parser.add_argument("--name", type=str, help="Name of the tenant common variable", required=True)
        upsert_parser.add_argument("--value", type=str, help="Value of the tenant common variable", required=True)

    @staticmethod
    def _check_tenant(tenant_id: str):
        if not Tenant.objects.filter(id=tenant_id).exists():
            raise ValueError(f"Tenant {tenant_id} is not existed")

    def handle(self, *args, **options):
        tenant_id = options["tenant_id"]
        # 校验
        self._check_tenant(tenant_id)

        # 子命令路由
        handler = getattr(self, f"handle_{options['subcommand']}", None)
        if handler:
            handler(tenant_id, options)
        else:
            raise CommandError(f"Subcommand {options['subcommand']} is not supported")

    def handle_list(self, tenant_id: str, options):
        """列出所有公共变量"""
        common_variables = TenantCommonVariable.objects.filter(tenant_id=tenant_id).values("name", "value")
        output = {v["name"]: v["value"] for v in common_variables}

        self.stdout.write("Tenant common variables:\n")
        for key, value in output.items():
            self.stdout.write(f"{key} = {value}")

    def handle_get(self, tenant_id: str, options):
        """获取指定公共变量"""
        name = options["name"]
        common_variable = TenantCommonVariable.objects.filter(tenant_id=tenant_id, name=name).first()
        if not common_variable:
            raise ValueError(f"Tenant common variable {name} not found")

        self.stdout.write(f"{common_variable.value}\n")

    def handle_delete(self, tenant_id: str, options):
        """删除指定公共变量"""
        name = options["name"]
        deleted, _ = TenantCommonVariable.objects.filter(tenant_id=tenant_id, name=name).delete()
        if deleted == 0:
            raise ValueError(f"Tenant common variable {name} not found")

        self.stdout.write(f"Tenant common variable {name} deleted\n")

    def handle_upsert(self, tenant_id: str, options):
        """更新或创建指定公共变量"""
        name = options["name"]
        value = options["value"]

        common_variable, _ = TenantCommonVariable.objects.update_or_create(
            tenant_id=tenant_id,
            name=name,
            defaults={"value": value},
        )

        self.stdout.write(f"Tenant common variable {name} upserted with value: {value}\n")
