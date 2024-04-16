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
from typing import Any, Dict

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceDepartment, DataSourceDepartmentRelation
from bkuser.apps.tenant.models import Tenant, TenantDepartment


class TenantDataSourceSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="数据源 ID")
    type = serializers.CharField(help_text="数据源类型")
    plugin_id = serializers.CharField(help_text="数据源插件 ID")


class TenantListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名称")
    logo = serializers.SerializerMethodField(help_text="租户 Logo")

    def get_logo(self, obj: Tenant) -> str:
        return obj.logo or settings.DEFAULT_TENANT_LOGO


class TenantRetrieveOutputSLZ(TenantListOutputSLZ):
    data_source = serializers.SerializerMethodField(help_text="真实用户数据源信息")

    class Meta:
        ref_name = "organization.TenantRetrieveOutputSLZ"

    @swagger_serializer_method(serializer_or_field=TenantDataSourceSLZ())
    def get_data_source(self, obj: Tenant) -> Dict[str, Any] | None:
        data_source = DataSource.objects.filter(owner_tenant_id=obj.id, type=DataSourceTypeEnum.REAL).first()
        if not data_source:
            return None

        return {"id": data_source.id, "type": data_source.type, "plugin_id": data_source.plugin_id}


class TenantDepartmentListInputSLZ(serializers.Serializer):
    parent_department_id = serializers.IntegerField(help_text="父部门 ID（为 0 表示根部门）", default=0)

    def validate_parent_department_id(self, parent_dept_id: int) -> int:
        if (
            parent_dept_id
            and not TenantDepartment.objects.filter(
                id=parent_dept_id,
                tenant_id=self.context["tenant_id"],
            ).exists()
        ):
            raise ValidationError(_("指定的父部门在当前租户中不存在"))

        return parent_dept_id


class TenantDepartmentListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门 ID")
    name = serializers.CharField(help_text="部门名称")
    has_children = serializers.BooleanField(help_text="是否有子部门")


def _validate_duplicate_dept_name_in_ancestors(
    parent_relation: DataSourceDepartmentRelation | None, name: str
) -> None:
    # 已经是根部门了，不需要继续判断祖先
    if not parent_relation:
        return

    ancestor_dept_ids = parent_relation.get_ancestors(include_self=True).values_list("department_id", flat=True)
    if DataSourceDepartment.objects.filter(id__in=ancestor_dept_ids, name=name).exists():
        raise ValidationError(_("上级部门中存在同名部门：{}").format(name))


class TenantDepartmentCreateInputSLZ(serializers.Serializer):
    parent_department_id = serializers.IntegerField(help_text="父部门 ID（为 0 表示根部门）", default=0)
    name = serializers.CharField(help_text="部门名称")

    def validate_parent_department_id(self, parent_dept_id: int) -> int:
        if (
            parent_dept_id
            and not TenantDepartment.objects.filter(
                id=parent_dept_id,
                tenant_id=self.context["tenant_id"],
            ).exists()
        ):
            raise ValidationError(_("指定的父部门在当前租户中不存在"))

        return parent_dept_id

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        dept_name = attrs["name"]

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

        data_source_dept_ids = DataSourceDepartmentRelation.objects.filter(
            parent=parent_dept_relation, data_source=self.context["data_source"]
        ).values_list("department_id", flat=True)

        if DataSourceDepartment.objects.filter(id__in=data_source_dept_ids, name=dept_name).exists():
            raise ValidationError(_("指定的父部门下已存在同名部门：{}").format(dept_name))

        # 在祖先部门中检查是否有同名的
        _validate_duplicate_dept_name_in_ancestors(parent_dept_relation, dept_name)

        return attrs


class TenantDepartmentCreateOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门 ID")


class TenantDepartmentUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="部门名称")

    def validate_name(self, name: str) -> str:
        tenant_dept: TenantDepartment = self.context["tenant_dept"]
        data_source_dept = tenant_dept.data_source_department

        parent_dept_relation = DataSourceDepartmentRelation.objects.get(
            department=data_source_dept, data_source=tenant_dept.data_source
        ).parent

        # Q: 为什么不使用 parent_dept_relation.get_children
        # A: 如果是根部门，parent_dept_relation 为 None，会报错 :)
        brother_data_source_dept_ids = (
            DataSourceDepartmentRelation.objects.filter(
                parent=parent_dept_relation, data_source=tenant_dept.data_source
            )
            .exclude(department=data_source_dept)
            .values_list("department_id", flat=True)
        )
        if DataSourceDepartment.objects.filter(id__in=brother_data_source_dept_ids, name=name).exists():
            raise ValidationError(_("父部门下已存在同名部门：{}").format(name))

        # 在祖先部门中检查是否有同名的
        _validate_duplicate_dept_name_in_ancestors(parent_dept_relation, name)

        return name
