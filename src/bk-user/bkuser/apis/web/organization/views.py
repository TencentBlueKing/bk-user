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
import logging
from collections import defaultdict

from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apis.web.organization.serializers import (
    TenantDepartmentChildrenListOutputSLZ,
    TenantDepartmentUserSearchInputSLZ,
    TenantListOutputSLZ,
    TenantUserListOutputSLZ,
    TenantUserRetrieveOutputSLZ,
    TenantUserSearchInputSLZ,
)
from bkuser.apis.web.tenant.serializers import TenantRetrieveOutputSLZ, TenantUpdateInputSLZ
from bkuser.apps.data_source.models import DataSource, DataSourceDepartmentRelation, DataSourceDepartmentUserRelation
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.constants import TenantStatus
from bkuser.apps.tenant.models import Tenant, TenantDepartment, TenantUser
from bkuser.biz.data_source import DataSourceHandler
from bkuser.biz.data_source_organization import DataSourceDepartmentHandler
from bkuser.biz.tenant import (
    TenantDepartmentHandler,
    TenantEditableInfo,
    TenantFeatureFlag,
    TenantHandler,
    TenantUserHandler,
)
from bkuser.common.error_codes import error_codes
from bkuser.common.views import ExcludePatchAPIViewMixin

logger = logging.getLogger(__name__)


class TenantListApi(CurrentUserTenantMixin, generics.ListAPIView):
    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["tenant-organization"],
        operation_description="租户列表",
        responses={status.HTTP_200_OK: TenantListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        cur_tenant_id = self.get_current_tenant_id()
        # TODO 目前只有当前用户登录的租户，后续需要考虑跨租户协同的情况
        tenant_ids = [cur_tenant_id]

        tenants = Tenant.objects.filter(id__in=tenant_ids)
        # 将当前登录用户所在的租户置顶
        tenants = sorted(tenants, key=lambda t: t.id != cur_tenant_id)

        # 先获取租户有权限的数据源（包括拥有的以及协同的）
        data_sources = DataSourceHandler.get_tenant_available_data_sources(cur_tenant_id)
        # FIXME (su) 协同的租户不一定会提供根部门，应该改成从协同范围表中获取协同的顶层数据源部门 ID
        root_data_source_dept_ids = (
            DataSourceDepartmentRelation.objects.root_nodes()
            .filter(data_source_id__in=[ds.id for ds in data_sources])
            .values_list("department_id", flat=True)
        )
        # 指定租户 ID，可以确保即使跨租户协同，也是在指定的协同范围内的
        root_tenant_depts = TenantDepartment.objects.filter(
            tenant_id=cur_tenant_id,
            data_source_department_id__in=root_data_source_dept_ids,
        ).select_related("data_source_department")

        sub_dept_ids_map = DataSourceDepartmentHandler.get_sub_data_source_dept_ids_map(root_data_source_dept_ids)

        tenant_root_depts_map = defaultdict(list)
        for tenant in tenants:
            for dept in root_tenant_depts:
                tenant_root_depts_map[tenant.id].append(
                    {
                        "id": dept.id,
                        "name": dept.data_source_department.name,
                        "has_children": bool(len(sub_dept_ids_map[dept.data_source_department_id])),
                    }
                )

        return Response(
            TenantListOutputSLZ(tenants, many=True, context={"tenant_root_depts_map": tenant_root_depts_map}).data
        )


class TenantRetrieveUpdateApi(ExcludePatchAPIViewMixin, CurrentUserTenantMixin, generics.RetrieveUpdateAPIView):
    queryset = Tenant.objects.all()
    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
    serializer_class = TenantRetrieveOutputSLZ
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["tenant-organization"],
        operation_description="单个租户详情",
        responses={status.HTTP_200_OK: TenantRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["tenant-organization"],
        operation_description="更新租户",
        request_body=TenantUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = TenantUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant = self.get_object()
        if tenant.status != TenantStatus.ENABLED:
            raise error_codes.TENANT_NOT_ENABLED.f(_("仅可编辑已启用的租户配置信息"))

        tenant_info = TenantEditableInfo(
            name=data["name"],
            logo=data["logo"] or "",
            feature_flags=TenantFeatureFlag(**data["feature_flags"]),
        )

        TenantHandler.update_with_managers(tenant.id, tenant_info, data["manager_ids"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserListApi(CurrentUserTenantMixin, generics.ListAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
    serializer_class = TenantUserListOutputSLZ

    @swagger_auto_schema(
        tags=["tenant-organization"],
        operation_description="租户下用户列表",
        query_serializer=TenantUserSearchInputSLZ(),
        responses={status.HTTP_200_OK: TenantUserListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        slz = TenantUserSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        cur_tenant_id = self.get_current_tenant_id()
        # 当前租户可获取的数据源信息（含协同，不含禁用）
        data_sources = DataSourceHandler.get_tenant_available_data_sources(cur_tenant_id)
        # 指定租户 ID，可以确保即使跨租户协同，也是在指定的协同范围内的
        # FIXME (su) 协同获得的租户用户，也不一定就是该租户拥有的数据源部门的，需要根据所属数据源所属租户做区分
        tenant_users = (
            TenantUser.objects.filter(tenant_id=cur_tenant_id, data_source__in=data_sources)
            .select_related("data_source_user")
            .order_by("data_source_user__username")
        )

        if keyword := data.get("keyword"):
            tenant_users = tenant_users.filter(
                Q(data_source_user__username__icontains=keyword) | Q(data_source_user__full_name__icontains=keyword)
            )
        tenant_users = self.paginate_queryset(tenant_users)
        context = {
            "tenant_user_depts_map": TenantUserHandler.get_tenant_users_depts_map(cur_tenant_id, tenant_users),
        }
        return self.get_paginated_response(TenantUserListOutputSLZ(tenant_users, many=True, context=context).data)


class TenantDepartmentChildrenListApi(CurrentUserTenantMixin, generics.ListAPIView):
    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
    serializer_class = TenantDepartmentChildrenListOutputSLZ
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return TenantDepartment.objects.filter(tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["tenant-organization"],
        operation_description="租户部门的二级子部门列表",
        responses={status.HTTP_200_OK: TenantDepartmentChildrenListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        tenant_dept = self.get_object()

        data_source_id = tenant_dept.data_source_department.data_source_id
        # 即使数据源被停用，也是可以查看组织架构信息的
        if not DataSource.objects.filter(id=data_source_id).exists():
            raise error_codes.DATA_SOURCE_NOT_EXISTS

        tenant_dept_children_infos = TenantDepartmentHandler.get_tenant_dept_children_infos(tenant_dept)
        return Response(TenantDepartmentChildrenListOutputSLZ(tenant_dept_children_infos, many=True).data)


class TenantDepartmentUserListApi(CurrentUserTenantMixin, generics.ListAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    def get_queryset(self):
        cur_tenant_id = self.get_current_tenant_id()
        return TenantDepartment.objects.filter(tenant_id=cur_tenant_id).select_related("data_source_department")

    @swagger_auto_schema(
        tags=["tenant-organization"],
        operation_description="租户部门下用户列表",
        query_serializer=TenantDepartmentUserSearchInputSLZ(),
        responses={status.HTTP_200_OK: TenantUserListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        slz = TenantDepartmentUserSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant_dept = self.get_object()

        data_source_id = tenant_dept.data_source_department.data_source_id
        # 即使数据源被停用，也是可以查看组织架构信息的
        if not DataSource.objects.filter(id=data_source_id).exists():
            raise error_codes.DATA_SOURCE_NOT_EXISTS

        # 需要通过数据源部门 - 用户关系反查租户部门用户信息，且需要支持递归查询子孙部门用户
        data_source_dept_ids = [tenant_dept.data_source_department_id]
        if data["recursive"]:
            rel = DataSourceDepartmentRelation.objects.get(department_id=tenant_dept.data_source_department_id)
            data_source_dept_ids = rel.get_descendants(include_self=True).values_list("department_id", flat=True)

        data_source_user_ids = DataSourceDepartmentUserRelation.objects.filter(
            department_id__in=data_source_dept_ids,
        ).values_list("user_id", flat=True)

        tenant_users = (
            # 指定租户 ID，可以确保即使跨租户协同，也是在指定的协同范围内的
            TenantUser.objects.filter(tenant=tenant_dept.tenant, data_source_user_id__in=data_source_user_ids)
            .select_related("data_source_user")
            .order_by("data_source_user__username")
        )

        if keyword := data.get("keyword"):
            tenant_users = tenant_users.filter(
                Q(data_source_user__username__icontains=keyword) | Q(data_source_user__full_name__icontains=keyword)
            )

        tenant_users = self.paginate_queryset(tenant_users)
        context = {
            "tenant_user_depts_map": TenantUserHandler.get_tenant_users_depts_map(tenant_dept.tenant_id, tenant_users),
        }
        return self.get_paginated_response(TenantUserListOutputSLZ(tenant_users, many=True, context=context).data)


class TenantUserRetrieveApi(generics.RetrieveAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
    serializer_class = TenantUserRetrieveOutputSLZ

    @swagger_auto_schema(
        tags=["tenant-organization"],
        operation_description="租户部门下单个用户详情",
        responses={status.HTTP_200_OK: TenantUserRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
