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
from collections import defaultdict
from typing import Dict

from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apis.web.organization.serializers import (
    OptionalTenantDepartmentListInputSLZ,
    OptionalTenantDepartmentListOutputSLZ,
    TenantDepartmentCreateInputSLZ,
    TenantDepartmentCreateOutputSLZ,
    TenantDepartmentListInputSLZ,
    TenantDepartmentListOutputSLZ,
    TenantDepartmentSearchInputSLZ,
    TenantDepartmentSearchOutputSLZ,
    TenantDepartmentUpdateInputSLZ,
)
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
)
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.models import Tenant, TenantDepartment
from bkuser.common.error_codes import error_codes
from bkuser.common.views import ExcludePatchAPIViewMixin
from bkuser.utils.uuid import generate_uuid


class TenantDepartmentListCreateApi(CurrentUserTenantMixin, generics.ListCreateAPIView):
    """获取租户部门列表 / 创建租户部门"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    pagination_class = None

    def get_queryset(self):
        slz = TenantDepartmentListInputSLZ(
            data=self.request.query_params,
            context={"tenant_id": self.get_current_tenant_id()},
        )
        slz.is_valid(raise_exception=True)
        parent_dept_id = slz.validated_data["parent_department_id"]

        # 如果指定父部门 ID，则获取其子部门
        if parent_dept_id:
            return self._get_children_depts(parent_dept_id)

        # 如果没有指定父部门 ID，则获取指定租户的根部门
        return self._get_root_depts()

    def _get_root_depts(self) -> QuerySet[TenantDepartment]:
        owner_tenant_id = self.kwargs["id"]
        # 获取指定租户的数据源，通过数据源部门关系查询部门列表
        data_source = DataSource.objects.filter(
            owner_tenant_id=owner_tenant_id,
            type=DataSourceTypeEnum.REAL,
        ).first()
        if not data_source:
            return TenantDepartment.objects.none()

        root_data_source_dept_ids = (
            DataSourceDepartmentRelation.objects.root_nodes()
            .filter(data_source=data_source)
            .values_list("department_id", flat=True)
        )
        return TenantDepartment.objects.filter(
            tenant_id=self.get_current_tenant_id(),
            data_source__owner_tenant_id=owner_tenant_id,
            data_source_department_id__in=root_data_source_dept_ids,
        ).select_related("data_source_department")

    def _get_children_depts(self, parent_dept_id: int) -> QuerySet[TenantDepartment]:
        # 获取的部门是属于当前用户租户的，但是可根据 kwargs["id"] 指定其来源是本租户 / 协作的租户
        filters = {
            "tenant_id": self.get_current_tenant_id(),
            "data_source__owner_tenant_id": self.kwargs["id"],
        }
        # 指定的父部门不存在，直接返回 None
        tenant_dept = TenantDepartment.objects.filter(id=parent_dept_id, **filters).first()
        if not tenant_dept:
            return TenantDepartment.objects.none()

        relation = DataSourceDepartmentRelation.objects.filter(
            department_id=tenant_dept.data_source_department_id,
        ).first()
        if not relation:
            return TenantDepartment.objects.none()

        # 根据关系表查询该父部门的子部门列表
        data_source_dept_ids = relation.get_children().values_list("department_id", flat=True)
        return TenantDepartment.objects.filter(
            data_source_department_id__in=data_source_dept_ids, **filters
        ).select_related("data_source_department")

    @staticmethod
    def _get_dept_has_children_map(tenant_depts: QuerySet[TenantDepartment]) -> Dict[int, bool]:
        """获取部门是否有子部门的信息"""
        parent_data_source_dept_ids = [tenant_dept.data_source_department_id for tenant_dept in tenant_depts]

        child_data_source_dept_ids_map = defaultdict(list)
        # 注：当前 MPTT 模型中，parent_id 等价于 parent__department_id
        for rel in DataSourceDepartmentRelation.objects.filter(parent_id__in=parent_data_source_dept_ids):
            child_data_source_dept_ids_map[rel.parent_id].append(rel.department_id)

        return {
            tenant_dept.id: bool(child_data_source_dept_ids_map.get(tenant_dept.data_source_department_id))
            for tenant_dept in tenant_depts
        }

    @swagger_auto_schema(
        tags=["organization.department"],
        operation_description="获取指定租户在当前租户的部门列表",
        query_serializer=TenantDepartmentListInputSLZ(),
        responses={status.HTTP_200_OK: TenantDepartmentListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        tenant_depts = self.get_queryset()
        has_children_map = self._get_dept_has_children_map(tenant_depts)
        tenant_dept_infos = [
            {
                "id": tenant_dept.id,
                "name": tenant_dept.data_source_department.name,
                "has_children": has_children_map.get(tenant_dept.id, False),
            }
            for tenant_dept in tenant_depts
        ]
        return Response(TenantDepartmentListOutputSLZ(tenant_dept_infos, many=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["organization.department"],
        operation_description="创建租户部门",
        query_serializer=TenantDepartmentCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: TenantDepartmentCreateOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        current_tenant_id = self.get_current_tenant_id()
        if self.kwargs["id"] != current_tenant_id:
            raise error_codes.TENANT_DEPARTMENT_CREATE_FAILED.f(_("仅可创建属于当前租户的部门"))

        # 必须存在实名用户数据源才可以创建租户部门
        data_source = DataSource.objects.filter(
            owner_tenant_id=current_tenant_id, type=DataSourceTypeEnum.REAL
        ).first()
        if not data_source:
            raise error_codes.TENANT_DEPARTMENT_CREATE_FAILED.f(_("租户数据源不存在"))
        if not data_source.is_local:
            raise error_codes.TENANT_DEPARTMENT_CREATE_FAILED.f(_("仅本地数据源支持创建部门"))

        slz = TenantDepartmentCreateInputSLZ(
            data=request.data, context={"tenant_id": current_tenant_id, "data_source": data_source}
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 则将部门关联到父部门（根部门也需要关联到 None）
        parent_dept_relation = None
        if parent_tenant_dept_id := data["parent_department_id"]:
            # 从租户部门 ID 找数据源部门
            parent_data_source_dept = TenantDepartment.objects.get(
                tenant_id=current_tenant_id, id=parent_tenant_dept_id
            ).data_source_department
            parent_dept_relation = DataSourceDepartmentRelation.objects.get(
                department=parent_data_source_dept, data_source=data_source
            )

        with transaction.atomic():
            data_source_dept = DataSourceDepartment.objects.create(
                data_source=data_source, code=generate_uuid(), name=data["name"]
            )
            # 将新的数据源部门和父部门关联起来
            DataSourceDepartmentRelation.objects.create(
                department=data_source_dept,
                parent=parent_dept_relation,
                data_source=data_source,
            )
            # FIXME (su) 支持租户协同后，要把协同的租户部门也创建出来
            tenant_dept = TenantDepartment.objects.create(
                tenant_id=current_tenant_id,
                data_source_department=data_source_dept,
                data_source=data_source,
            )

        return Response(TenantDepartmentCreateOutputSLZ(tenant_dept).data, status=status.HTTP_201_CREATED)


class TenantDepartmentUpdateDestroyApi(
    CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.UpdateAPIView, generics.DestroyAPIView
):
    """编辑 / 删除租户部门"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[TenantDepartment]:
        return TenantDepartment.objects.filter(tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["organization.department"],
        operation_description="更新租户部门",
        query_serializer=TenantDepartmentUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        tenant_dept = self.get_object()
        if not (tenant_dept.data_source.is_local and tenant_dept.data_source.is_real_type):
            raise error_codes.TENANT_DEPARTMENT_UPDATE_FAILED.f(_("仅本地数据源支持更新部门"))
        if tenant_dept.data_source.owner_tenant_id != self.get_current_tenant_id():
            raise error_codes.TENANT_DEPARTMENT_UPDATE_FAILED.f(_("仅可更新属于当前租户的部门"))

        slz = TenantDepartmentUpdateInputSLZ(data=request.data, context={"tenant_dept": tenant_dept})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant_dept.data_source_department.name = data["name"]
        tenant_dept.data_source_department.save(update_fields=["name", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["organization.department"],
        operation_description="删除租户部门",
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        """删除租户部门：要求该部门下的用户都被迁移走，否则无法删除"""
        tenant_dept = self.get_object()
        if not (tenant_dept.data_source.is_local and tenant_dept.data_source.is_real_type):
            raise error_codes.TENANT_DEPARTMENT_DELETE_FAILED.f(_("仅真实用户类型的本地数据源支持删除部门"))

        data_source_dept = tenant_dept.data_source_department
        # 注：这里不应该使用 filter().first()，因为就算是根部门也会
        # 有 parent=None 的 relation，如果存在脏数据应该暴露出来而不是悄悄处理
        dept_relation = DataSourceDepartmentRelation.objects.get(department_id=data_source_dept.id)
        # 该部门及其所有子部门的 ID 集合
        data_source_dept_ids = dept_relation.get_descendants(include_self=True).values_list("department_id", flat=True)
        # 查询关联表确保不存在用户
        if DataSourceDepartmentUserRelation.objects.filter(department_id__in=data_source_dept_ids).exists():
            raise error_codes.TENANT_DEPARTMENT_DELETE_FAILED.f(_("该部门或其子部门下存在用户，无法删除"))

        with transaction.atomic():
            # 连带协同产生的租户部门还有子部门都给你删咯
            TenantDepartment.objects.filter(data_source_department_id__in=data_source_dept_ids).delete()
            # 所有的子数据源部门都要删除
            DataSourceDepartment.objects.filter(id__in=data_source_dept_ids).delete()
            # 涉及到的部门关联边都要删除，然后再重建
            DataSourceDepartmentRelation.objects.filter(department_id__in=data_source_dept_ids).delete()
            DataSourceDepartmentRelation.objects.partial_rebuild(dept_relation.tree_id)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantDepartmentSearchApi(CurrentUserTenantMixin, generics.ListAPIView):
    """搜索租户部门"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    pagination_class = None
    # 限制搜索结果，只提供前 N 条记录，如果展示不完全，需要用户细化搜索条件
    search_limit = settings.ORGANIZATION_SEARCH_API_LIMIT

    def get_queryset(self) -> QuerySet[TenantDepartment]:
        slz = TenantDepartmentSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        keyword = slz.validated_data["keyword"]

        return TenantDepartment.objects.filter(
            tenant_id=self.get_current_tenant_id(), data_source_department__name__icontains=keyword
        ).select_related("data_source", "data_source_department")[: self.search_limit]

    def _get_dept_organization_path_map(self, tenant_depts: QuerySet[TenantDepartment]) -> Dict[int, str]:
        """获取租户部门的组织路径信息"""
        data_source_dept_ids = [tenant_dept.data_source_department_id for tenant_dept in tenant_depts]

        # 数据源部门 ID -> 组织路径
        org_path_map = {}
        for dept_relation in DataSourceDepartmentRelation.objects.filter(
            department_id__in=data_source_dept_ids
        ).select_related("department"):
            dept_names = list(
                dept_relation.get_ancestors(include_self=True).values_list("department__name", flat=True)
            )
            org_path_map[dept_relation.department_id] = "/".join(dept_names)

        # 租户部门 ID -> 组织路径
        return {
            dept.id: org_path_map.get(dept.data_source_department_id, dept.data_source_department.name)
            for dept in tenant_depts
        }

    @swagger_auto_schema(
        tags=["organization.department"],
        operation_description="搜索租户部门",
        query_serializer=TenantDepartmentSearchInputSLZ(),
        responses={status.HTTP_200_OK: TenantDepartmentSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        tenant_depts = self.get_queryset()
        context = {
            "tenant_name_map": {tenant.id: tenant.name for tenant in Tenant.objects.all()},
            "org_path_map": self._get_dept_organization_path_map(tenant_depts),
        }
        resp_data = TenantDepartmentSearchOutputSLZ(tenant_depts, many=True, context=context).data
        return Response(resp_data, status=status.HTTP_200_OK)


class OptionalTenantDepartmentListApi(CurrentUserTenantMixin, generics.ListAPIView):
    """可选租户部门列表（下拉框数据用）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    serializer_class = OptionalTenantDepartmentListOutputSLZ

    def get_queryset(self) -> QuerySet[TenantDepartment]:
        # FIXME (su) 和 search api 一样，需要限制 limit = 20, 不分页，然后还需要提供组织路径
        slz = OptionalTenantDepartmentListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        queryset = TenantDepartment.objects.filter(
            data_source__owner_tenant_id=self.get_current_tenant_id()
        ).select_related("data_source_department")
        if kw := params.get("keyword"):
            queryset = queryset.filter(data_source_department__name__icontains=kw)

        return queryset.order_by("id")

    @swagger_auto_schema(
        tags=["organization.department"],
        operation_description="可选部门列表",
        query_serializer=OptionalTenantDepartmentListInputSLZ(),
        responses={status.HTTP_200_OK: OptionalTenantDepartmentListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
