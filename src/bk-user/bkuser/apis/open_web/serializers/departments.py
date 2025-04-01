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
from typing import Any, Dict

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.biz.tenant import TenantUserHandler
from bkuser.common.serializers import StringArrayField


class TenantDepartmentSearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", min_length=1, max_length=64)
    owner_tenant_id = serializers.CharField(help_text="所属租户 ID", required=False, allow_blank=True, default="")


class TenantDepartmentSearchOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门 ID")
    name = serializers.CharField(help_text="部门名称", source="data_source_department.name")
    owner_tenant_id = serializers.CharField(help_text="所属租户 ID", source="data_source.owner_tenant_id")
    organization_path = serializers.SerializerMethodField(help_text="组织路径")
    has_child = serializers.SerializerMethodField(help_text="是否有子部门")
    has_user = serializers.SerializerMethodField(help_text="是否有用户")

    def get_organization_path(self, obj: TenantDepartment) -> str:
        return self.context["org_path_map"][obj.data_source_department_id]

    def get_has_child(self, obj: TenantDepartment) -> bool:
        return self.context["has_child_map"][obj.data_source_department_id]

    def get_has_user(self, obj: TenantDepartment) -> bool:
        return self.context["has_user_map"][obj.data_source_department_id]


class TenantDepartmentChildrenListInputSLZ(serializers.Serializer):
    owner_tenant_id = serializers.CharField(help_text="所属租户 ID", required=False)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        department_id = self.context["department_id"]
        owner_tenant_id = attrs.get("owner_tenant_id")

        if not department_id and not owner_tenant_id:
            raise ValidationError(_("当 department_id 未提供时，必须指定 owner_tenant_id"))

        return attrs


class TenantDepartmentChildrenListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门ID")
    name = serializers.CharField(help_text="部门名称", source="data_source_department.name")
    has_child = serializers.SerializerMethodField(help_text="是否有子部门")
    has_user = serializers.SerializerMethodField(help_text="是否有用户")

    def get_has_child(self, obj: TenantDepartment) -> bool:
        return self.context["has_child_map"][obj.data_source_department_id]

    def get_has_user(self, obj: TenantDepartment) -> bool:
        return self.context["has_user_map"][obj.data_source_department_id]


class TenantDepartmentUserListInputSLZ(serializers.Serializer):
    owner_tenant_id = serializers.CharField(help_text="归属租户 ID", required=False)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        department_id = self.context["department_id"]
        owner_tenant_id = attrs.get("owner_tenant_id")

        if not department_id and not owner_tenant_id:
            raise ValidationError(_("当 department_id 未提供时，必须指定 owner_tenant_id"))

        return attrs


class TenantDepartmentUserListOutputSLZ(serializers.Serializer):
    bk_username = serializers.CharField(help_text="蓝鲸用户唯一标识", source="id")
    login_name = serializers.CharField(help_text="企业内用户唯一标识", source="data_source_user.username")
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)


class TenantDepartmentLookupInputSLZ(serializers.Serializer):
    department_ids = StringArrayField(help_text="部门ID，多个使用逗号分隔", max_items=100)


class TenantDepartmentLookupOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门 ID")
    name = serializers.CharField(help_text="部门名称", source="data_source_department.name")
    owner_tenant_id = serializers.CharField(help_text="所属租户 ID", source="data_source.owner_tenant_id")
    organization_path = serializers.SerializerMethodField(help_text="组织路径")

    def get_organization_path(self, obj: TenantDepartment) -> str:
        return self.context["org_path_map"][obj.data_source_department_id]
