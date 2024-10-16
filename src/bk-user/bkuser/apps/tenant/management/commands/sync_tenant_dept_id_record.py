# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.core.management.base import BaseCommand

from bkuser.apps.tenant.models import TenantDepartment, TenantDepartmentIDRecord


class Command(BaseCommand):
    """
    同步租户部门 ID 记录

    $ python manage.py sync_tenant_dept_id_record

    执行时机：首次部署 & 数据迁移完成后执行一次，可重入
    """

    def handle(self, *args, **options):
        # 直接全部删除
        TenantDepartmentIDRecord.objects.all().delete()
        # 再根据租户部门数据，重新创建
        records = [
            TenantDepartmentIDRecord(
                id=dept.id,
                tenant_id=dept.tenant_id,
                data_source_id=dept.data_source_id,
                code=dept.data_source_department.code,
                tenant_department_id=dept.id,
            )
            for dept in TenantDepartment.objects.select_related("data_source_department")
        ]
        TenantDepartmentIDRecord.objects.bulk_create(records, batch_size=250)
