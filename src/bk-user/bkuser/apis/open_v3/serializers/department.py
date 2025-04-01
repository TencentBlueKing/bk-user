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

from rest_framework import serializers

from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.biz.tenant import TenantUserHandler
from bkuser.common.serializers import StringArrayField


class AncestorSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="祖先部门 ID")
    name = serializers.CharField(help_text="祖先部门名称")

    class Meta:
        ref_name = "open_v3.department.AncestorSLZ"


class TenantDepartmentRetrieveInputSLZ(serializers.Serializer):
    with_ancestors = serializers.BooleanField(label="是否包括祖先部门", required=False, default=False)


class TenantDepartmentRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门 ID")
    name = serializers.CharField(help_text="部门名称")
    ancestors = serializers.ListField(help_text="祖先部门列表", required=False, child=AncestorSLZ(), allow_empty=True)


class TenantDepartmentListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门 ID")
    name = serializers.CharField(help_text="部门名称", source="data_source_department.name")
    parent_id = serializers.SerializerMethodField(help_text="父部门 ID", allow_null=True)

    def get_parent_id(self, obj: TenantDepartment) -> int | None:
        return self.context["parent_id_map"].get(obj.id)


class TenantDepartmentDescendantListInputSLZ(serializers.Serializer):
    max_level = serializers.IntegerField(
        help_text="递归子部门的最大相对 Level 层级", required=False, default=1, min_value=1
    )


class TenantDepartmentDescendantListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门 ID")
    name = serializers.CharField(help_text="部门名称", source="data_source_department.name")
    parent_id = serializers.SerializerMethodField(help_text="父部门 ID")

    def get_parent_id(self, obj: TenantDepartment) -> int | None:
        return self.context["parent_id_map"].get(obj.id)


class TenantDepartmentUserListOutputSLZ(serializers.Serializer):
    bk_username = serializers.CharField(help_text="蓝鲸用户唯一标识", source="id")
    full_name = serializers.CharField(help_text="姓名", source="data_source_user.full_name")
    display_name = serializers.SerializerMethodField(help_text="用户展示名称")

    def get_display_name(self, obj: TenantUser) -> str:
        return TenantUserHandler.generate_tenant_user_display_name(obj)


class TenantDepartmentLookupInputSLZ(serializers.Serializer):
    department_ids = StringArrayField(
        help_text="部门唯一标识，多个使用逗号分隔",
        max_items=50,
    )
    with_organization_path = serializers.BooleanField(help_text="是否返回组织路径", required=False, default=False)


class TenantDepartmentLookupOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门 ID")
    name = serializers.CharField(help_text="部门名称", source="data_source_department.name")
    organization_path = serializers.SerializerMethodField(help_text="组织路径")

    def get_organization_path(self, obj: TenantDepartment) -> str:
        return self.context["org_path_map"].get(obj.data_source_department_id, "")
