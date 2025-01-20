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
from typing import Any, Dict, List

from drf_yasg.utils import swagger_auto_schema
from mptt.querysets import TreeQuerySet
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from bkuser.apis.open_v3.mixins import OpenApiCommonMixin
from bkuser.apis.open_v3.serializers.department import (
    TenantDepartmentChildrenListInputSLZ,
    TenantDepartmentChildrenListOutputSLZ,
    TenantDepartmentRetrieveInputSLZ,
    TenantDepartmentRetrieveOutputSLZ,
)
from bkuser.apps.data_source.models import DataSourceDepartment, DataSourceDepartmentRelation
from bkuser.apps.tenant.models import TenantDepartment
from bkuser.biz.organization import DataSourceDepartmentHandler


class TenantDepartmentRetrieveApi(OpenApiCommonMixin, generics.RetrieveAPIView):
    """
    获取部门信息（支持是否包括祖先部门）
    """

    queryset = TenantDepartment.objects.all()
    lookup_url_kwarg = "id"
    serializer_class = TenantDepartmentRetrieveOutputSLZ

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


class TenantDepartmentChildrenListApi(OpenApiCommonMixin, generics.ListAPIView):
    """
    获取部门下的子部门列表信息（支持递归）
    """

    serializer_class = TenantDepartmentChildrenListOutputSLZ

    @swagger_auto_schema(
        tags=["open_v3.department"],
        operation_id="list_department_children",
        operation_description="查询部门下的子部门列表",
        query_serializer=TenantDepartmentChildrenListInputSLZ(),
        responses={status.HTTP_200_OK: TenantDepartmentChildrenListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        slz = TenantDepartmentChildrenListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant_department = get_object_or_404(
            TenantDepartment.objects.filter(tenant_id=self.tenant_id), id=kwargs["id"]
        )

        relation = DataSourceDepartmentRelation.objects.filter(
            department_id=tenant_department.data_source_department_id
        ).first()

        # 计算绝对层级 Level
        absolute_level = relation.level + data["level"]
        # 按层级 Level 递归查询该部门的子部门
        child_ids = relation.get_descendants().filter(level=absolute_level).values_list("department_id", flat=True)

        # 获取子部门列表信息
        dept_infos = self.list_dept_infos(child_ids)

        return self.get_paginated_response(
            TenantDepartmentChildrenListOutputSLZ(self.paginate_queryset(dept_infos), many=True).data
        )

    def list_dept_infos(self, child_ids: TreeQuerySet[int]) -> List[Dict[str, Any]]:
        """
        获取子部门列表信息
        """

        # 预加载部门对应的租户部门
        dept_id_map = dict(
            TenantDepartment.objects.filter(
                data_source_department_id__in=child_ids, tenant_id=self.tenant_id
            ).values_list("data_source_department_id", "id")
        )

        # 预加载部门对应的名称
        dept_name_map = dict(DataSourceDepartment.objects.filter(id__in=child_ids).values_list("id", "name"))

        # 组装数据
        return [
            {"id": dept_id_map[dept_id], "name": dept_name_map[dept_id]}
            for dept_id in child_ids
            if dept_id in dept_id_map
        ]
