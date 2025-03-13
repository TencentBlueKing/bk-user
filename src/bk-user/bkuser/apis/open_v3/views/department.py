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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from bkuser.apis.open_v3.mixins import OpenApiCommonMixin
from bkuser.apis.open_v3.serializers.department import (
    TenantDepartmentDescendantListInputSLZ,
    TenantDepartmentDescendantListOutputSLZ,
    TenantDepartmentListOutputSLZ,
    TenantDepartmentRetrieveInputSLZ,
    TenantDepartmentRetrieveOutputSLZ,
    TenantDepartmentUserListOutputSLZ,
)
from bkuser.apps.data_source.models import DataSourceDepartmentRelation, DataSourceDepartmentUserRelation
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.biz.organization import DataSourceDepartmentHandler, TenantDepartmentHandler


class TenantDepartmentRetrieveApi(OpenApiCommonMixin, generics.RetrieveAPIView):
    """
    获取部门信息（支持是否包括祖先部门）
    """

    lookup_url_kwarg = "id"

    def get_queryset(self):
        return TenantDepartment.objects.filter(tenant_id=self.tenant_id, data_source_id=self.real_data_source_id)

    @swagger_auto_schema(
        tags=["open_v3.department"],
        operation_id="retrieve_department",
        operation_description="查询部门信息",
        query_serializer=TenantDepartmentRetrieveInputSLZ(),
        responses={status.HTTP_200_OK: TenantDepartmentRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        slz = TenantDepartmentRetrieveInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant_department = self.get_object()

        info = {
            "id": tenant_department.id,
            "name": tenant_department.data_source_department.name,
        }

        if data["with_ancestors"]:
            # 查询部门对应的祖先部门列表
            ancestor_ids = DataSourceDepartmentHandler.get_dept_ancestors(tenant_department.data_source_department_id)
            tenant_depts = TenantDepartment.objects.filter(
                data_source_department_id__in=ancestor_ids, tenant_id=tenant_department.tenant_id
            ).select_related("data_source_department")

            info["ancestors"] = [{"id": d.id, "name": d.data_source_department.name} for d in tenant_depts]

        return Response(TenantDepartmentRetrieveOutputSLZ(info).data)


class TenantDepartmentListApi(OpenApiCommonMixin, generics.ListAPIView):
    """
    获取部门列表
    """

    @swagger_auto_schema(
        tags=["open_v3.department"],
        operation_id="list_department",
        operation_description="查询部门列表",
        responses={status.HTTP_200_OK: TenantDepartmentListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        depts = TenantDepartment.objects.select_related("data_source_department").filter(
            tenant=self.tenant_id, data_source_id=self.real_data_source_id
        )

        # 分页
        page = self.paginate_queryset(depts)

        # 查询 parent
        parent_id_map = TenantDepartmentHandler.get_tenant_department_parent_id_map(self.tenant_id, page)

        return self.get_paginated_response(
            TenantDepartmentListOutputSLZ(page, many=True, context={"parent_id_map": parent_id_map}).data
        )


class TenantDepartmentDescendantListApi(OpenApiCommonMixin, generics.ListAPIView):
    """
    获取部门下的子部门列表信息（支持递归）
    """

    @swagger_auto_schema(
        tags=["open_v3.department"],
        operation_id="list_department_descendant",
        operation_description="查询部门下的子部门列表",
        query_serializer=TenantDepartmentDescendantListInputSLZ(),
        responses={status.HTTP_200_OK: TenantDepartmentDescendantListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        slz = TenantDepartmentDescendantListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 若传入的 department_id 为 0，则获取根部门
        if not kwargs["id"]:
            data_source_dept_ids = (
                DataSourceDepartmentRelation.objects.root_nodes()
                .filter(data_source_id=self.real_data_source_id)
                .values_list("department_id", flat=True)
            )

            depts = TenantDepartment.objects.filter(
                tenant_id=self.tenant_id,
                data_source_department_id__in=data_source_dept_ids,
            ).select_related("data_source_department")

        else:
            tenant_department = get_object_or_404(
                TenantDepartment.objects.filter(tenant_id=self.tenant_id, data_source_id=self.real_data_source_id),
                id=kwargs["id"],
            )

            relation = DataSourceDepartmentRelation.objects.get(
                department_id=tenant_department.data_source_department_id
            )

            # 计算绝对层级 Level
            level = relation.level + data["max_level"]
            # 按层级 Level 递归查询该部门的子部门
            descendant_ids = (
                relation.get_descendants().filter(level__lte=level).values_list("department_id", flat=True)
            )

            depts = TenantDepartment.objects.filter(
                data_source_department_id__in=descendant_ids, tenant_id=self.tenant_id
            ).select_related("data_source_department")

        # 分页
        page = self.paginate_queryset(depts)

        # 查询 parent
        parent_id_map = TenantDepartmentHandler.get_tenant_department_parent_id_map(self.tenant_id, page)

        return self.get_paginated_response(
            TenantDepartmentDescendantListOutputSLZ(page, many=True, context={"parent_id_map": parent_id_map}).data
        )


class TenantDepartmentUserListApi(OpenApiCommonMixin, generics.ListAPIView):
    serializer_class = TenantDepartmentUserListOutputSLZ

    def get_queryset(self):
        tenant_department = get_object_or_404(
            TenantDepartment.objects.filter(tenant_id=self.tenant_id, data_source_id=self.real_data_source_id),
            id=self.kwargs["id"],
        )
        user_ids = DataSourceDepartmentUserRelation.objects.filter(
            department_id=tenant_department.data_source_department_id
        ).values_list("user_id", flat=True)

        return (
            TenantUser.objects.select_related("data_source_user")
            .filter(data_source_user_id__in=user_ids, tenant_id=self.tenant_id)
            .only("id", "data_source_user__full_name")
        )

    @swagger_auto_schema(
        tags=["open_v3.department"],
        operation_id="list_department_user",
        operation_description="查询部门的用户列表",
        responses={status.HTTP_200_OK: TenantDepartmentUserListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
