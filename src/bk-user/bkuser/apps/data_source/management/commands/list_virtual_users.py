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
from django.core.management import BaseCommand
from django.db.models import Q

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceUser


class Command(BaseCommand):
    """
    查询租户的虚拟用户
    $ python manage.py list_virtual_users
    """

    help = "List virtual users of specified tenant"

    def add_arguments(self, parser):
        parser.add_argument("--tenant_id", type=str, required=True, help="Tenant ID")
        parser.add_argument("--username", type=str, help="Filter by username (optional)")

    def handle(self, *args, **options):
        tenant_id = options["tenant_id"]
        username_filter = options.get("username")

        # 获取租户的虚拟数据源
        data_source = DataSource.objects.filter(owner_tenant_id=tenant_id, type=DataSourceTypeEnum.VIRTUAL).first()

        if not data_source:
            raise ValueError(f"Tenant {tenant_id} has no virtual data source")

        query = Q(data_source=data_source)
        if username_filter:
            query &= Q(username=username_filter)

        # 查询虚拟用户
        virtual_users = DataSourceUser.objects.filter(query)

        if not virtual_users.exists():
            self.stdout.write("No virtual users found")
            return

        if username_filter:
            user = virtual_users.first()
            self.stdout.write(
                f"Username: {user.username}\n"
                f"Full Name: {user.full_name}\n"
                f"Email: {user.email or ''}\n"
                f"Phone: {user.phone or ''}\n"
                f"Phone Country Code: {user.phone_country_code or ''}\n"
                f"Created At: {user.created_at}"
            )
        else:
            self.stdout.write(f"Virtual users of tenant {tenant_id} (Total: {virtual_users.count()}):")
            self.stdout.write("-" * 80)
            for user in virtual_users:
                self.stdout.write(
                    f"Username: {user.username}\n"
                    f"Full Name: {user.full_name}\n"
                    f"Email: {user.email or ''}\n"
                    f"Phone: {user.phone or ''}\n"
                    f"Phone Country Code: {user.phone_country_code or ''}\n"
                    f"Created At: {user.created_at}\n"
                    f"------------------------------"
                )
