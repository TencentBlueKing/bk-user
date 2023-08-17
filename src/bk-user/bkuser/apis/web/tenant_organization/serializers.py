# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging

from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from bkuser.apps.data_source.models import DataSourceDepartmentRelation
from bkuser.biz.tenant import TenantDepartmentHandler

logger = logging.getLogger(__name__)


class TenantDepartmentOutputSchema(serializers.Serializer):
    id = serializers.IntegerField(help_text="租户部门ID")
    name = serializers.CharField(help_text="部门名称")
    has_children = serializers.BooleanField(help_text="子部门信息")


class TenantDepartmentChildrenListOutputSLZ(serializers.Serializer):
    departments = serializers.SerializerMethodField()

    def _list_departments_info(self, current_tenant_id, departments):
        data = []
        # 此处已经过滤出和当前租户绑定组织
        tenant_department_map = TenantDepartmentHandler.get_tenant_departments_info_map(
            current_tenant_id, [item.department.id for item in departments]
        )
        for item in departments:
            # NOTE：协同数据源，部分根部门并未授权到当前部门
            tenant_department = tenant_department_map.get(item.department.id, None)
            if not tenant_department:
                logger.info(f"DataSourceDepartment<{item.department.id}> does not bind Tenant<{current_tenant_id}>")
                continue
            data.append(tenant_department.model_dump())
        return data

    def _get_children_department(self, instance):
        data_source_department_id = instance.data_source_department_id
        department = DataSourceDepartmentRelation.objects.get(department_id=data_source_department_id)
        children = department.get_children()
        return self._list_departments_info(instance.tenant_id, children)

    @swagger_serializer_method(serializer_or_field=TenantDepartmentOutputSchema(many=True))
    def get_departments(self, instance):
        return self._get_children_department(instance)
