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
from typing import List

from django.conf import settings
from drf_yasg.utils import swagger_serializer_method
from mptt.templatetags.mptt_tags import cache_tree_children
from rest_framework import serializers

from bkuser.apis.web.tenant.serializers import TenantFeatureFlagSLZ, TenantRetrieveManagerOutputSchema
from bkuser.apps.data_source.models import DataSourceDepartmentRelation
from bkuser.biz.data_source import DataSourceHandler
from bkuser.biz.tenant import TenantDepartmentHandler

logger = logging.getLogger(__name__)


class TenantDepartmentOutputSchema(serializers.Serializer):
    id = serializers.IntegerField(help_text="租户部门ID")
    name = serializers.CharField(help_text="部门名称")
    has_children = serializers.BooleanField(help_text="是否有子部门")


class TenantUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.CharField(help_text="租户 Logo", required=False)
    manager_ids = serializers.ListField(child=serializers.CharField(), help_text="租户用户 ID 列表", allow_empty=False)
    feature_flags = TenantFeatureFlagSLZ(help_text="租户特性集")


class TenantsListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户组织节点ID")
    name = serializers.CharField(help_text="租户组织节点名称名")
    logo = serializers.SerializerMethodField(help_text="租户 Logo")
    departments = serializers.SerializerMethodField(help_text="租户下每个数据源的根组织")

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

    def _get_root_departments(self, instance):
        # 协同数据源，是以租户的形式展示,转换为当前租户
        tenant_id = instance.id
        current_tenant_id = self.context["current_tenant_id"]
        # 获取旗下根部门的各个数据源
        # TODO 协同数据源，是以租户的形式展示，考虑怎么获取授权的数据源？
        # 通过获取数据源的根节点
        data_sources = DataSourceHandler.get_data_source_map_by_owner([tenant_id])[tenant_id]
        data_sources_ids = [i.id for i in data_sources]
        # 获取租户下所有数据员的根组织
        data_source_root_departments = cache_tree_children(
            DataSourceDepartmentRelation.objects.filter(level=0, data_source_id__in=data_sources_ids)
        )
        return self._list_departments_info(current_tenant_id, data_source_root_departments)

    def get_logo(self, instance) -> str:
        return instance.logo or settings.DEFAULT_TENANT_LOGO

    @swagger_serializer_method(serializer_or_field=TenantDepartmentOutputSchema(many=True))
    def get_departments(self, instance):
        return self._get_root_departments(instance)


class TenantsRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户ID")
    name = serializers.CharField(help_text="租户名")
    logo = serializers.SerializerMethodField(help_text="租户 Logo")
    feature_flags = TenantFeatureFlagSLZ(help_text="租户特性集")
    managers = serializers.SerializerMethodField()

    @swagger_serializer_method(serializer_or_field=TenantRetrieveManagerOutputSchema(many=True))
    def get_managers(self, instance) -> List[dict]:
        tenant_manager_map = self.context["tenant_manager_map"]
        managers = tenant_manager_map.get(instance.id, [])
        return [
            {
                "id": i.id,
                **i.data_source_user.model_dump(
                    include={"username", "full_name", "email", "phone", "phone_country_code"}
                ),
            }
            for i in managers
        ]

    def get_logo(self, instance) -> str:
        return instance.logo or settings.DEFAULT_TENANT_LOGO
