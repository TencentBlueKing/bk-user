# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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

from typing import Any, Dict

from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.models import DataSourceDepartment, DataSourceDepartmentRelation
from bkuser.apps.tenant.models import TenantDepartment


def _validate_parent_dept_id(parent_dept_id: int, tenant_id: str) -> int:
    if (
        parent_dept_id
        and not TenantDepartment.objects.filter(
            id=parent_dept_id,
            tenant_id=tenant_id,
        ).exists()
    ):
        raise ValidationError(_("指定的父部门在当前租户中不存在"))

    return parent_dept_id


class TenantDepartmentListInputSLZ(serializers.Serializer):
    parent_department_id = serializers.IntegerField(help_text="父部门 ID（为 0 表示获取根部门）", default=0)

    def validate_parent_department_id(self, parent_dept_id: int) -> int:
        return _validate_parent_dept_id(parent_dept_id, self.context["tenant_id"])


class TenantDepartmentListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门 ID")
    name = serializers.CharField(help_text="部门名称")
    has_children = serializers.BooleanField(help_text="是否有子部门")


def _validate_duplicate_dept_name_in_brothers(
    parent_relation: DataSourceDepartmentRelation | None,
    name: str,
    data_source_department: DataSourceDepartment,
) -> None:
    # 获取兄弟部门的数据源部门 ID，排除自己
    # Q: 为什么不使用 parent_dept_relation.get_children
    # A: 如果是根部门，parent_dept_relation 为 None，会报错 :)
    brother_data_source_dept_ids = (
        DataSourceDepartmentRelation.objects.filter(
            parent=parent_relation, data_source=data_source_department.data_source
        )
        .exclude(department=data_source_department)
        .values_list("department_id", flat=True)
    )

    if DataSourceDepartment.objects.filter(id__in=brother_data_source_dept_ids, name=name).exists():
        raise ValidationError(_("指定的父部门下已存在同名部门：{}").format(name))


def _validate_duplicate_dept_name_in_ancestors(
    parent_relation: DataSourceDepartmentRelation | None, name: str
) -> None:
    # 没有父部门 -> 已经是根部门，不需要继续判断祖先
    if not parent_relation:
        return

    ancestor_dept_ids = parent_relation.get_ancestors(include_self=True).values_list("department_id", flat=True)
    if DataSourceDepartment.objects.filter(id__in=ancestor_dept_ids, name=name).exists():
        raise ValidationError(_("上级部门中存在同名部门：{}").format(name))


class TenantDepartmentCreateInputSLZ(serializers.Serializer):
    parent_department_id = serializers.IntegerField(help_text="父部门 ID（为 0 表示创建根部门）", default=0)
    name = serializers.CharField(help_text="部门名称")

    def validate_parent_department_id(self, parent_dept_id: int) -> int:
        return _validate_parent_dept_id(parent_dept_id, self.context["tenant_id"])

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        dept_name = attrs["name"]
        if "/" in dept_name:
            raise ValidationError(_("部门名称不允许包含斜杠(/)"))

        parent_dept_relation = None
        if parent_tenant_dept_id := attrs["parent_department_id"]:
            # 租户部门 ID -> 数据源部门
            parent_data_source_dept = TenantDepartment.objects.get(
                id=parent_tenant_dept_id, tenant_id=self.context["tenant_id"]
            ).data_source_department
            # 数据源部门 -> 父部门关系表节点
            parent_dept_relation = DataSourceDepartmentRelation.objects.get(
                department=parent_data_source_dept, data_source=self.context["data_source"]
            )

        brother_data_source_dept_ids = DataSourceDepartmentRelation.objects.filter(
            parent=parent_dept_relation, data_source=self.context["data_source"]
        ).values_list("department_id", flat=True)

        if DataSourceDepartment.objects.filter(id__in=brother_data_source_dept_ids, name=dept_name).exists():
            raise ValidationError(_("指定的父部门下已存在同名部门：{}").format(dept_name))

        # 在祖先部门中检查是否有同名的
        _validate_duplicate_dept_name_in_ancestors(parent_dept_relation, dept_name)

        return attrs


class TenantDepartmentCreateOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门 ID")


class TenantDepartmentUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="部门名称")

    def validate_name(self, name: str) -> str:
        if "/" in name:
            raise ValidationError(_("部门名称不允许包含斜杠(/)"))

        tenant_dept: TenantDepartment = self.context["tenant_dept"]
        data_source_dept = tenant_dept.data_source_department

        parent_dept_relation = DataSourceDepartmentRelation.objects.get(
            department=data_source_dept, data_source=tenant_dept.data_source
        ).parent

        # 在兄弟部门中检查是否有同名的
        _validate_duplicate_dept_name_in_brothers(parent_dept_relation, name, data_source_dept)

        # 在祖先部门中检查是否有同名的
        _validate_duplicate_dept_name_in_ancestors(parent_dept_relation, name)

        return name


class TenantDepartmentSearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", min_length=2, max_length=64)


class TenantDepartmentSearchOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门 ID")
    name = serializers.CharField(help_text="部门名称", source="data_source_department.name")
    tenant_id = serializers.CharField(help_text="部门来源租户 ID", source="data_source.owner_tenant_id")
    tenant_name = serializers.SerializerMethodField(help_text="部门来源租户名称")
    organization_path = serializers.SerializerMethodField(help_text="组织路径")

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_tenant_name(self, obj: TenantDepartment) -> str:
        return self.context["tenant_name_map"][obj.data_source.owner_tenant_id]

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_organization_path(self, obj: TenantDepartment) -> str:
        return self.context["org_path_map"].get(obj.id, obj.data_source_department.name)


class OptionalTenantDepartmentListInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", min_length=1, max_length=64, required=False)


class OptionalTenantDepartmentListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="租户部门 ID")
    name = serializers.CharField(help_text="部门名称", source="data_source_department.name")
    organization_path = serializers.SerializerMethodField(help_text="组织路径")

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_organization_path(self, obj: TenantDepartment) -> str:
        return self.context["org_path_map"].get(obj.id, obj.data_source_department.name)


class TenantDepartmentParentUpdateInputSLZ(serializers.Serializer):
    parent_department_id = serializers.IntegerField(help_text="目标父部门 ID（为 0 表示获取根部门）")

    def validate_parent_department_id(self, parent_dept_id: int) -> int:
        parent_dept_id = _validate_parent_dept_id(parent_dept_id, self.context["tenant_id"])

        if parent_dept_id == self.context["tenant_dept_id"]:
            raise ValidationError(_("自己不能成为自己的子部门"))

        data_source_dept = self.context["data_source_dept"]

        parent_dept_relation = None
        ancestor_dept_ids = []
        if parent_dept_id:
            # 租户部门 ID -> 数据源部门
            parent_data_source_dept = TenantDepartment.objects.get(
                id=parent_dept_id, tenant_id=self.context["tenant_id"]
            ).data_source_department
            # 数据源部门 -> 父部门关系表节点
            parent_dept_relation = DataSourceDepartmentRelation.objects.get(
                department=parent_data_source_dept, data_source=data_source_dept.data_source
            )
            # 获取目标部门的所有祖先部门 ID
            ancestor_dept_ids = parent_dept_relation.get_ancestors(include_self=False).values_list(
                "department_id", flat=True
            )

        if ancestor_dept_ids and data_source_dept.id in ancestor_dept_ids:
            raise ValidationError(_("不能移动至自己的子部门下"))

        # 在兄弟部门中检查是否有同名的
        _validate_duplicate_dept_name_in_brothers(parent_dept_relation, data_source_dept.name, data_source_dept)

        # 在祖先部门中检查是否有同名的
        _validate_duplicate_dept_name_in_ancestors(parent_dept_relation, data_source_dept.name)

        return parent_dept_id
