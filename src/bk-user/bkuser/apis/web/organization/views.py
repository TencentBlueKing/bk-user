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

from django.db.models import QuerySet
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apis.web.organization.serializers import (
    TenantDepartmentListInputSLZ,
    TenantDepartmentListOutputSLZ,
    TenantListOutputSLZ,
    TenantRetrieveOutputSLZ,
)
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceDepartmentRelation
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.models import Tenant, TenantDepartment


class CurrentTenantRetrieveApi(CurrentUserTenantMixin, generics.ListAPIView):
    """获取当前用户所在租户信息"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    def get_queryset(self):
        return Tenant.objects.filter(id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["organization"],
        operation_description="获取当前用户所在租户信息",
        responses={status.HTTP_200_OK: TenantRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return Response(TenantRetrieveOutputSLZ(self.get_object()), status=status.HTTP_200_OK)


class CollaborativeTenantListApi(CurrentUserTenantMixin, generics.ListAPIView):
    """获取当前租户的协作租户信息"""

    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    def get_queryset(self):
        # TODO (su) 目前是根据部门信息获取的协作租户 ID，后续可修改成根据协同策略获取？
        # 不过通过部门反查优点是一定有数据（协作策略已确认，但是未同步的情况）
        cur_tenant_id = self.get_current_tenant_id()
        depts = TenantDepartment.objects.filter(tenant_id=cur_tenant_id).exclude(
            data_source__owner_tenant_id=cur_tenant_id
        )
        collaborative_tenant_ids = set(depts.values_list("data_source__owner_tenant_id", flat=True))
        return Tenant.objects.filter(id__in=collaborative_tenant_ids)

    @swagger_auto_schema(
        tags=["organization"],
        operation_description="获取当前租户的协作租户信息",
        responses={status.HTTP_200_OK: TenantListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return Response(TenantListOutputSLZ(self.get_queryset(), many=True), status=status.HTTP_200_OK)


class TenantDepartmentListApi(CurrentUserTenantMixin, generics.ListAPIView):
    """获取当前租户部门信息"""

    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    def get_queryset(self):
        slz = TenantDepartmentListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        parent_dept_id = slz.validated_data["parent_department_id"]

        # 如果指定父部门 ID，则获取其子部门
        if parent_dept_id:
            return self._get_children_depts(parent_dept_id)

        # 如果没有指定父部门 ID，则获取指定租户的根部门
        return self._get_root_depts()

    def _get_root_depts(self) -> QuerySet[TenantDepartment]:
        # 获取指定租户的数据源，通过数据源部门关系查询部门列表
        data_source = DataSource.objects.filter(
            owner_tenant_id=self.kwargs["id"], type=DataSourceTypeEnum.REAL
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
            data_source__owner_tenant_id=self.kwargs["id"],
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
        parent_data_source_dept_ids = tenant_depts.values_list("data_source_department_id", flat=True)

        sub_data_source_dept_ids_map = defaultdict(list)
        # 注：当前 MPTT 模型中，parent_id 等价于 parent__department_id
        for rel in DataSourceDepartmentRelation.objects.filter(parent_id__in=parent_data_source_dept_ids):
            sub_data_source_dept_ids_map[rel.parent_id].append(rel.department_id)

        return {
            tenant_dept.id: bool(sub_data_source_dept_ids_map.get(tenant_dept.data_source_department_id))
            for tenant_dept in tenant_depts
        }

    @swagger_auto_schema(
        tags=["organization"],
        operation_description="获取当前租户部门列表",
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
        return Response(TenantDepartmentListOutputSLZ(tenant_dept_infos, many=True), status=status.HTTP_200_OK)
