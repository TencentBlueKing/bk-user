# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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

from bkuser.apis.open_web.constants import OpenWebApiEnum
from bkuser.apis.open_web.mixins import OpenWebApiCommonMixin
from bkuser.apis.open_web.pagination import gen_no_count_pagination_class
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
from bkuser.apis.open_web.throttle import open_web_api_throttle_class
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.biz.organization import TenantDepartmentHandler, TenantOrgPathHandler
from bkuser.biz.tenant import TenantUserDisplayNameHandler


class TenantDepartmentSearchApi(OpenWebApiCommonMixin, generics.ListAPIView):
    """
    搜索部门
    """

    throttle_classes = [open_web_api_throttle_class(OpenWebApiEnum.SEARCH_DEPARTMENT)]

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
            filters["data_source_id__in"] = DataSource.objects.filter(owner_tenant_id=tenant_id).values_list(
                "id", flat=True
            )

        queryset = TenantDepartment.objects.filter(**filters).select_related("data_source_department")

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
        data_source_department_ids = [dept.data_source_department_id for dept in tenant_depts]
        context = {
            "org_path_map": TenantOrgPathHandler.get_dept_organization_path_map(data_source_department_ids),
            "has_user_map": TenantDepartmentHandler.get_has_user_map(data_source_department_ids),
            "has_child_map": TenantDepartmentHandler.get_has_child_map(data_source_department_ids),
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

        # 如果指定部门 ID 不为 0，则获取其子部门
        if parent_department_id := self.kwargs["id"]:
            tenant_department = get_object_or_404(
                TenantDepartment.objects.filter(tenant_id=self.tenant_id), id=parent_department_id
            )

            relation = DataSourceDepartmentRelation.objects.get(
                department_id=tenant_department.data_source_department_id,
            )

            data_source_dept_ids = relation.get_children().values_list("department_id", flat=True)

        else:
            # 若指定部门 ID 为 0，则其子部门即为根部门
            data_sources = DataSource.objects.filter(
                owner_tenant_id=data["owner_tenant_id"], type=DataSourceTypeEnum.REAL
            )

            data_source_dept_ids = (
                DataSourceDepartmentRelation.objects.root_nodes()
                .filter(data_source__in=data_sources)
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
        data_source_department_ids = [dept.data_source_department_id for dept in tenant_depts]
        context = {
            "has_user_map": TenantDepartmentHandler.get_has_user_map(data_source_department_ids),
            "has_child_map": TenantDepartmentHandler.get_has_child_map(data_source_department_ids),
        }
        return Response(TenantDepartmentChildrenListOutputSLZ(tenant_depts, many=True, context=context).data)


class TenantDepartmentUserListApi(OpenWebApiCommonMixin, generics.ListAPIView):
    """
    获取指定部门下的用户列表
    """

    # 组织架构人员选择器目前仅支持“加载更多”交互，不依赖总条数，这里使用无 count 的分页处理
    pagination_class = gen_no_count_pagination_class(max_page_size=100)

    def get_queryset(self) -> QuerySet[TenantUser]:
        slz = TenantDepartmentUserListInputSLZ(
            data=self.request.query_params, context={"department_id": self.kwargs["id"]}
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        queryset = TenantUser.objects.filter(
            tenant_id=self.tenant_id, data_source__type=DataSourceTypeEnum.REAL
        ).select_related("data_source_user")

        # 若指定部门 ID 不为 0，则获取部门下的用户
        if department_id := self.kwargs["id"]:
            tenant_department = get_object_or_404(
                TenantDepartment.objects.filter(tenant_id=self.tenant_id),
                id=department_id,
            )

            user_ids = DataSourceDepartmentUserRelation.objects.filter(
                department_id=tenant_department.data_source_department_id
            ).values_list("user_id", flat=True)

            queryset = queryset.filter(data_source_user_id__in=user_ids)

        # 若指定部门 ID 为 0，则返回无部门的用户
        else:
            data_sources = DataSource.objects.filter(
                owner_tenant_id=data["owner_tenant_id"], type=DataSourceTypeEnum.REAL
            )
            # Q: 为什么这里使用 `data_source_user__datasourcedepartmentuserrelation__isnull=True`
            #    join + isnull 写法来获取无部门用户，而不是 `exclude(子查询)` 或在 Python 里做 set 差集？
            # A: 该写法会让数据库直接执行 LEFT JOIN ... IS NULL 来筛选“无部门用户”，
            #    能在一条 SQL 内完成过滤，避免 `exclude(子查询)` 带来的额外子查询复杂度，
            #    同时避免把大量用户 ID 拉到 Python 侧做集合运算造成的内存/网络开销（大数据量下耗时明显）。
            queryset = queryset.filter(
                data_source__in=data_sources,
                data_source_user__datasourcedepartmentuserrelation__isnull=True,
            )

        return queryset.order_by("id")

    @swagger_auto_schema(
        tags=["open_web.department"],
        operation_id="list_department_user",
        operation_description="查询部门的所属用户列表",
        query_serializer=TenantDepartmentUserListInputSLZ(),
        responses={status.HTTP_200_OK: TenantDepartmentUserListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        tenant_users = self.paginate_queryset(self.get_queryset())
        display_name_map = TenantUserDisplayNameHandler.batch_generate_tenant_user_display_name(tenant_users)
        slz = TenantDepartmentUserListOutputSLZ(
            tenant_users, many=True, context={"display_name_map": display_name_map}
        )
        return self.get_paginated_response(slz.data)


class TenantDepartmentLookupApi(OpenWebApiCommonMixin, generics.ListAPIView):
    """
    批量查询部门（包括协同部门）
    """

    pagination_class = None

    def get_queryset(self) -> QuerySet[TenantDepartment]:
        slz = TenantDepartmentLookupInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        return TenantDepartment.objects.filter(id__in=data["department_ids"], tenant_id=self.tenant_id).select_related(
            "data_source_department"
        )

    @swagger_auto_schema(
        tags=["open_web.department"],
        operation_id="lookup_department",
        operation_description="批量查询部门",
        query_serializer=TenantDepartmentLookupInputSLZ(),
        responses={status.HTTP_200_OK: TenantDepartmentLookupOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        tenant_depts = self.get_queryset()
        data_source_department_ids = [dept.data_source_department_id for dept in tenant_depts]
        context = {
            "org_path_map": TenantOrgPathHandler.get_dept_organization_path_map(data_source_department_ids),
        }
        return Response(TenantDepartmentLookupOutputSLZ(tenant_depts, many=True, context=context).data)
