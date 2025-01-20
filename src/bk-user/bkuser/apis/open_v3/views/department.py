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
from rest_framework.response import Response

from bkuser.apis.open_v3.mixins import OpenApiCommonMixin
from bkuser.apis.open_v3.serializers.department import (
    TenantDepartmentListOutputSLZ,
    TenantDepartmentRetrieveInputSLZ,
    TenantDepartmentRetrieveOutputSLZ,
)
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
        responses={status.HTTP_200_OK: TenantDepartmentListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        tenant_depts = TenantDepartment.objects.select_related("data_source_department__department_relation").filter(
            tenant=self.tenant_id
        )
        # 处理部门信息
        dept_info = DataSourceDepartmentHandler.list_dept_infos(self.paginate_queryset(tenant_depts))
        return self.get_paginated_response(TenantDepartmentListOutputSLZ(dept_info, many=True).data)
