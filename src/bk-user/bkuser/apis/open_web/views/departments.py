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
from typing import Any, Dict

from django.conf import settings
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apis.open_web.mixins import OpenWebApiCommonMixin, TenantDeptOrgPathMapMixin
from bkuser.apis.open_web.serializers.departments import (
    TenantDepartmentChildrenListInputSLZ,
    TenantDepartmentChildrenListOutputSLZ,
    TenantDepartmentLookupInputSLZ,
    TenantDepartmentLookupOutputSLZ,
    TenantDepartmentSearchInputSLZ,
    TenantDepartmentSearchOutputSLZ,
    TenantDepartmentUserListInputSLZ,
    TenantDepartmentUserListOutputSLZ,
)
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.biz.organization import TenantDepartmentHandler


class TenantDepartmentSearchApi(OpenWebApiCommonMixin, TenantDeptOrgPathMapMixin, generics.ListAPIView):
    """
    搜素部门
    """

    pagination_class = None

    # 限制搜索结果，只提供前 N 条记录，如果展示不完全，需要用户细化搜索条件
    search_limit = settings.SELECTOR_SEARCH_API_LIMIT

    def get_queryset(self) -> QuerySet[TenantDepartment]:
        slz = TenantDepartmentSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        filters: Dict[str, Any] = {
            "tenant_id": self.tenant_id,
            "data_source_department__name__icontains": data["keyword"],
        }

        # 若指定了 owner_tenant_id，则只搜索该租户下的用户；否则搜索本租户用户与协同租户用
        if tenant_id := data.get("owner_tenant_id"):
            filters["data_source__owner_tenant_id"] = tenant_id

        queryset = TenantDepartment.objects.filter(**filters).select_related("data_source_department", "data_source")

        return queryset[: self.search_limit]

    @swagger_auto_schema(
        tags=["open_web.department"],
        operation_id="search_department",
        operation_description="搜索部门",
        query_serializer=TenantDepartmentSearchInputSLZ(),
        responses={status.HTTP_200_OK: TenantDepartmentSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        tenant_depts = self.get_queryset()
        has_children_users_map = TenantDepartmentHandler.get_dept_has_children_users_map(tenant_depts)
        context = {
            "org_path_map": self._get_dept_organization_path_map(tenant_depts),
            "has_children_users_map": has_children_users_map,
        }
        return Response(TenantDepartmentSearchOutputSLZ(tenant_depts, many=True, context=context).data)


class TenantDepartmentChildrenListApi(OpenWebApiCommonMixin, generics.ListAPIView):
    """
    获取部门子部门（包括协同）列表
    """

    pagination_class = None

    def get_queryset(self) -> QuerySet[TenantDepartment]:
        slz = TenantDepartmentChildrenListInputSLZ(
            data=self.request.query_params, context={"department_id": self.kwargs["id"]}
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 如果指定了部门，则获取其子部门
        if parent_department_id := self.kwargs["id"]:
            tenant_department = get_object_or_404(
                TenantDepartment.objects.filter(tenant_id=self.tenant_id), id=parent_department_id
            )

            relation = DataSourceDepartmentRelation.objects.get(
                department_id=tenant_department.data_source_department_id,
            )

            data_source_dept_ids = relation.get_children().values_list("department_id", flat=True)

        else:
            # 若未指定则获取根部门
            data_source = get_object_or_404(
                DataSource.objects.filter(owner_tenant_id=data["owner_tenant_id"], type=DataSourceTypeEnum.REAL)
            )

            data_source_dept_ids = (
                DataSourceDepartmentRelation.objects.root_nodes()
                .filter(data_source=data_source)
                .values_list("department_id", flat=True)
            )

        return TenantDepartment.objects.filter(
            tenant_id=self.tenant_id,
            data_source_department_id__in=data_source_dept_ids,
        ).select_related("data_source_department")

    @swagger_auto_schema(
        tags=["open_web.department"],
        operation_id="list_department_child",
        operation_description="获取指定部门（包括协同）的子部门列表",
        query_serializer=TenantDepartmentChildrenListInputSLZ(),
        responses={status.HTTP_200_OK: TenantDepartmentChildrenListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        tenant_depts = self.get_queryset()
        has_children_users_map = TenantDepartmentHandler.get_dept_has_children_users_map(tenant_depts)
        tenant_dept_infos = [
            {
                "id": tenant_dept.id,
                "name": tenant_dept.data_source_department.name,
                "has_child": has_children_users_map[tenant_dept.id]["has_child"],
                "has_user": has_children_users_map[tenant_dept.id]["has_user"],
            }
            for tenant_dept in tenant_depts
        ]
        return Response(TenantDepartmentChildrenListOutputSLZ(tenant_dept_infos, many=True).data)


class TenantDepartmentUserListApi(OpenWebApiCommonMixin, generics.ListAPIView):
    """
    获取指定部门下的用户列表
    """

    pagination_class = None

    serializer_class = TenantDepartmentUserListOutputSLZ

    def get_queryset(self) -> QuerySet[TenantUser]:
        slz = TenantDepartmentUserListInputSLZ(
            data=self.request.query_params, context={"department_id": self.kwargs["id"]}
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        queryset = (
            TenantUser.objects.filter(tenant_id=self.tenant_id, data_source__type=DataSourceTypeEnum.REAL)
            .select_related("data_source_user")
            .only("id", "data_source_user__username", "data_source_user__full_name")
        )

        # 若指定了部门，则获取部门下的用户
        if department_id := self.kwargs["id"]:
            tenant_department = get_object_or_404(
                TenantDepartment.objects.filter(tenant_id=self.tenant_id),
                id=department_id,
            )

            user_ids = DataSourceDepartmentUserRelation.objects.filter(
                department_id=tenant_department.data_source_department_id
            ).values_list("user_id", flat=True)

            queryset = queryset.filter(data_source_user_id__in=user_ids)

        # 否则返回无部门的用户
        else:
            data_source = get_object_or_404(
                DataSource.objects.filter(owner_tenant_id=data["owner_tenant_id"], type=DataSourceTypeEnum.REAL)
            )
            user_ids = DataSourceDepartmentUserRelation.objects.filter(data_source=data_source).values_list(
                "user_id", flat=True
            )
            queryset = queryset.exclude(data_source_user_id__in=user_ids)

        return queryset

    @swagger_auto_schema(
        tags=["open_web.department"],
        operation_id="list_department_user",
        operation_description="查询部门的所属用户列表",
        query_serializer=TenantDepartmentUserListInputSLZ(),
        responses={status.HTTP_200_OK: TenantDepartmentUserListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TenantDepartmentLookupApi(OpenWebApiCommonMixin, TenantDeptOrgPathMapMixin, generics.ListAPIView):
    """
    批量查询部门（包括协同部门）
    """

    pagination_class = None

    def get_queryset(self) -> QuerySet[TenantDepartment]:
        slz = TenantDepartmentLookupInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        filters: Dict[str, Any] = {"tenant_id": self.tenant_id, "id__in": data["department_ids"]}

        if owner_tenant_id := data.get("owner_tenant_id"):
            filters["data_source__owner_tenant_id"] = owner_tenant_id

        return TenantDepartment.objects.filter(**filters).select_related("data_source_department", "data_source")

    @swagger_auto_schema(
        tags=["open_web.department"],
        operation_id="lookup_department",
        operation_description="批量查询部门",
        query_serializer=TenantDepartmentLookupInputSLZ(),
        responses={status.HTTP_200_OK: TenantDepartmentLookupOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        tenant_depts = self.get_queryset()
        context = {
            "org_path_map": self._get_dept_organization_path_map(tenant_depts),
        }
        return Response(TenantDepartmentLookupOutputSLZ(tenant_depts, many=True, context=context).data)
