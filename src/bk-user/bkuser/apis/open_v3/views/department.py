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

from django.db.models import QuerySet
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apis.open_v3.mixins import OpenApiCommonMixin
from bkuser.apis.open_v3.serializers.department import (
    TenantDepartmentListInputSLZ,
    TenantDepartmentListOutputSLZ,
    TenantDepartmentRetrieveInputSLZ,
    TenantDepartmentRetrieveOutputSLZ,
)
from bkuser.apps.data_source.models import DataSourceDepartment
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


class TenantDepartmentListApi(OpenApiCommonMixin, generics.ListAPIView):
    """
    获取部门列表
    """

    serializer_class = TenantDepartmentListOutputSLZ

    @swagger_auto_schema(
        tags=["open_v3.department"],
        operation_id="list_department",
        operation_description="查询部门列表",
        query_serializer=TenantDepartmentListInputSLZ(),
        responses={status.HTTP_200_OK: TenantDepartmentListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        slz = TenantDepartmentListInputSLZ(data=self.request.query_params, context={"tenant_id": self.tenant_id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 获取过滤后的查询集并进行分页
        tenant_depts = self.paginate_queryset(self.get_filter_queryset(data))

        # 处理部门信息
        dept_info = self._get_depts_info(tenant_depts)

        return self.get_paginated_response(TenantDepartmentListOutputSLZ(dept_info, many=True).data)

    def get_filter_queryset(self, data: Dict[str, Any]) -> QuerySet:
        """
        根据查询参数过滤部门
        """
        tenant_depts = TenantDepartment.objects.select_related("data_source_department__department_relation").filter(
            tenant=self.tenant_id
        )

        parent_id = data.get("parent_id")
        # 若没有指定查询字段，则直接返回
        if not parent_id:
            return tenant_depts

        # 若根据父部门 ID 进行精确查询，则需要先获取到对应的数据源部门 ID，然后通过部门关系表定位子部门
        ds_parent_id = (
            TenantDepartment.objects.filter(id=parent_id, tenant_id=self.tenant_id)
            .values_list("data_source_department_id", flat=True)
            .first()
        )

        return tenant_depts.filter(data_source_department__department_relation__parent=ds_parent_id)

    @staticmethod
    def _get_depts_info(tenant_depts: List[TenantDepartment]) -> List[Dict[str, Any]]:
        """
        根据过滤后的数据获取部门信息
        """

        # 预加载部门对应的租户部门
        tenant_dept_id_map = {
            (data_source_dept_id, tenant_id): dept_id
            for (data_source_dept_id, tenant_id, dept_id) in TenantDepartment.objects.values_list(
                "data_source_department_id", "tenant_id", "id"
            )
        }

        # 获取数据源部门 ID
        data_source_dept_ids = {dept.data_source_department_id for dept in tenant_depts}

        # 预加载部门对应的名称
        dept_name_map = dict(
            DataSourceDepartment.objects.filter(id__in=data_source_dept_ids).values_list("id", "name")
        )

        # 组装数据
        return [
            {
                "id": dept.id,
                "name": dept_name_map[dept.data_source_department_id],
                "parent_id": tenant_dept_id_map.get(
                    (dept.data_source_department.department_relation.parent_id, dept.tenant_id)
                ),
            }
            for dept in tenant_depts
        ]
