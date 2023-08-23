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

from django.conf import settings
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from bkuser.apps.tenant.models import Tenant

logger = logging.getLogger(__name__)


class TenantDepartmentOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="租户部门ID")
    name = serializers.CharField(help_text="部门名称")
    has_children = serializers.BooleanField(help_text="是否有子部门")


class TenantListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户ID")
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.SerializerMethodField(help_text="租户 Logo")
    departments = serializers.SerializerMethodField(help_text="租户下每个数据源的根组织")

    def get_logo(self, instance: Tenant) -> str:
        return instance.logo or settings.DEFAULT_TENANT_LOGO

    @swagger_serializer_method(serializer_or_field=TenantDepartmentOutputSLZ(many=True))
    def get_departments(self, instance: Tenant):
        departments = self.context["tenant_root_departments_map"].get(instance.id) or []
        return [item.model_dump(include={"id", "name", "has_children"}) for item in departments]


class TenantDepartmentChildrenListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="租户部门ID")
    name = serializers.CharField(help_text="部门名称")
    has_children = serializers.BooleanField(help_text="是否有子部门")
