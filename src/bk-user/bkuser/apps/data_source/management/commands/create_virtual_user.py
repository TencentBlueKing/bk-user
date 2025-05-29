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
from django.db import transaction

from bkuser import settings
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceUser


class Command(BaseCommand):
    """
    租户创建或修改虚拟用户
    $ python manage.py create_virtual_user
    """

    def add_arguments(self, parser):
        parser.add_argument("--tenant_id", type=str, required=True, help="Tenant ID")
        parser.add_argument("--username", type=str, required=True, help="Username of the virtual user.")
        parser.add_argument("--full_name", type=str, required=True, help="Full name of the virtual user.")
        parser.add_argument("--email", type=str, help="Email address of the virtual user (optional).")
        parser.add_argument("--phone", type=str, help="Phone number of the virtual user (optional).")
        parser.add_argument(
            "--phone_country_code",
            type=str,
            default=settings.DEFAULT_PHONE_COUNTRY_CODE,
            help="Country code of the phone number (optional, defaults to system default).",
        )

    def handle(self, *args, **options):
        tenant_id = options["tenant_id"]
        username = options["username"]

        data_source = DataSource.objects.filter(
            type=DataSourceTypeEnum.VIRTUAL,
            owner_tenant_id=tenant_id,
        ).first()

        if not data_source:
            raise ValueError(f"Tenant {tenant_id} has no virtual data source")

        with transaction.atomic():
            # 创建数据源用户
            user, created = DataSourceUser.objects.get_or_create(
                data_source=data_source,
                username=username,
                defaults={
                    "full_name": options.get("full_name"),
                    "email": options.get("email"),
                    "phone": options.get("phone"),
                    "phone_country_code": options.get("phone_country_code"),
                    "code": username,
                    "logo": settings.DEFAULT_TENANT_LOGO,
                },
            )

            if not created:
                # 检查并准备需要更新的字段
                update_fields = {}
                if options.get("full_name") != user.full_name:
                    update_fields["full_name"] = options.get("full_name")
                if options.get("email") and options["email"] != user.email:
                    update_fields["email"] = options["email"]
                if options.get("phone") and options["phone"] != user.phone:
                    update_fields["phone"] = options["phone"]
                if options.get("phone_country_code") and options["phone_country_code"] != user.phone_country_code:
                    update_fields["phone_country_code"] = options["phone_country_code"]

                if update_fields:
                    DataSourceUser.objects.filter(id=user.id).update(**update_fields)
                    self.stdout.write(f"Virtual user '{username}' updated fields: {', '.join(update_fields.keys())}")
                else:
                    self.stdout.write(f"Virtual user '{username}' already exists (no changes found)")
            else:
                self.stdout.write(
                    f"Virtual user with username '{username}' has been successfully created in data source."
                )
