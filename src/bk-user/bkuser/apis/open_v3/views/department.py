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
from typing import List

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apis.open_v3.mixins import OpenApiCommonMixin
from bkuser.apis.open_v3.serializers.department import (
    TenantDepartmentRetrieveInputSLZ,
    TenantDepartmentRetrieveOutputSLZ,
)
from bkuser.apps.data_source.models import DataSourceDepartmentRelation
from bkuser.apps.tenant.models import TenantDepartment


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

        department_info = {
            "id": tenant_department.id,
            "name": tenant_department.data_source_department.name,
        }

        if data["with_ancestors"]:
            ancestor_ids = self._get_ancestors(tenant_department.data_source_department.id)
            ancestor_tenant_depts = TenantDepartment.objects.filter(
                data_source_department_id__in=ancestor_ids, tenant_id=tenant_department.tenant_id
            )
            department_info["ancestors"] = [
                {
                    "id": ancestor_tenant_dept.id,
                    "name": ancestor_tenant_dept.data_source_department.name,
                }
                for ancestor_tenant_dept in ancestor_tenant_depts
            ]

        return Response(TenantDepartmentRetrieveOutputSLZ(department_info).data)

    @staticmethod
    def _get_ancestors(dept_id: int) -> List[int]:
        """
        获取某个部门的祖先部门 ID 列表
        """
        relation = DataSourceDepartmentRelation.objects.filter(department_id=dept_id).first()
        # 若该部门不存在祖先节点，则返回空列表
        if not relation:
            return []
        # 返回的祖先部门默认以降序排列，从根祖先部门 -> 直接祖先部门
        return list(relation.get_ancestors().values_list("department_id", flat=True))
