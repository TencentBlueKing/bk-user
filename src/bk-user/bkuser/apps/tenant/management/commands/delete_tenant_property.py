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

from bkuser.apps.tenant.models import Tenant


class Command(BaseCommand):
    """
    删除租户公共属性
    $ python manage.py delete_tenant_property
    """

    def add_arguments(self, parser):
        parser.add_argument("--tenant_id", type=str, help="Tenant ID", required=True)
        parser.add_argument("--key", type=str, help="Property key", required=True)

    @staticmethod
    def _check_tenant(tenant_id: str):
        if not Tenant.objects.filter(id=tenant_id).exists():
            raise ValueError(f"Tenant {tenant_id} does not exist")

    def handle(self, *args, **options):
        tenant_id = options["tenant_id"]
        key = options["key"]

        self._check_tenant(tenant_id)
        tenant = Tenant.objects.get(id=tenant_id)

        deleted_count, _ = tenant.properties.filter(key=key).delete()

        if deleted_count == 0:
            raise ValueError(f"Key {key} is not exist in tenant {tenant.id} properties")

        self.stdout.write(f"Key {key} deleted from tenant {tenant.id} properties")
