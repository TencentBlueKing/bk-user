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

from django.db.models import Q
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
from bkuser.apps.data_source.models import DataSourceDepartmentRelation
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.models import Tenant, TenantDepartment, TenantUser
from bkuser.biz.data_source import DataSourceDepartmentHandler
from bkuser.biz.tenant import (
    TenantDepartmentHandler,
    TenantEditableBaseInfo,
    TenantFeatureFlag,
    TenantHandler,
    TenantUserHandler,
)
from bkuser.common.views import ExcludePatchAPIViewMixin

logger = logging.getLogger(__name__)


class TenantDepartmentUserListApi(CurrentUserTenantMixin, generics.ListAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
    serializer_class = TenantUserListOutputSLZ

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

        tenant_id = self.get_current_tenant_id()
        # 过滤出该租户部门的租户用户
        current_department_tenant_user_ids = TenantUserHandler.get_tenant_user_ids_by_tenant_department(
            tenant_id=tenant_id, tenant_department_id=self.kwargs["id"], recursive=data["recursive"]
        )

        # build response
        queryset = self.filter_queryset(self.get_queryset().filter(id__in=current_department_tenant_user_ids))
        if keyword := data.get("keyword"):
            queryset = queryset.select_related("data_source_user").filter(
                Q(data_source_user__username__icontains=keyword) | Q(data_source_user__full_name__icontains=keyword)
            )

        tenant_users = self.paginate_queryset(queryset)
        tenant_user_ids = [user.id for user in tenant_users]
        context = {
            "tenant_user_info_map": TenantUserHandler.list_tenant_user_by_id(tenant_user_ids),
            "tenant_user_departments_map": TenantUserHandler.get_tenant_user_departments_map_by_id(
                tenant_id, tenant_user_ids
            ),
        }
        serializer = TenantUserListOutputSLZ(tenant_users, many=True, context=context)
        return self.get_paginated_response(serializer.data)


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


class TenantListApi(CurrentUserTenantMixin, generics.ListAPIView):
    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["tenant-organization"],
        operation_description="租户列表",
        responses={status.HTTP_200_OK: TenantListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        current_tenant_id: str = self.get_current_tenant_id()

        # 获取当前租户以及有协同关系的租户
        # TODO 过滤出与当前租户有协同关系的租户
        queryset = Tenant.objects.filter(id__in=[current_tenant_id])

        # 将当前租户置顶
        # 通过比对租户id, 当等于当前登录用户的租户id，将其排序到查询集的顶部, 否则排序到查询集的底部
        sorted_queryset = sorted(queryset, key=lambda t: t.id != current_tenant_id)

        # 获取租户根组织
        tenant_root_departments_map = TenantDepartmentHandler.get_tenant_root_department_map_by_tenant_id(
            list(queryset.values_list("id", flat=True)), current_tenant_id
        )

        serializer = TenantListOutputSLZ(
            sorted_queryset, many=True, context={"tenant_root_departments_map": tenant_root_departments_map}
        )

        return Response(serializer.data)


class TenantRetrieveUpdateApi(ExcludePatchAPIViewMixin, CurrentUserTenantMixin, generics.RetrieveUpdateAPIView):
    queryset = Tenant.objects.all()
    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
    serializer_class = TenantRetrieveOutputSLZ
    lookup_url_kwarg = "id"

    def get_serializer_context(self):
        current_tenant_id = self.get_current_tenant_id()
        return {"tenant_manager_map": {current_tenant_id: TenantHandler.retrieve_tenant_managers(current_tenant_id)}}

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
        tenant_info = TenantEditableBaseInfo(
            name=data["name"], logo=data["logo"] or "", feature_flags=TenantFeatureFlag(**data["feature_flags"])
        )

        TenantHandler.update_with_managers(tenant.id, tenant_info, data["manager_ids"])
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        tenant_department = self.get_object()

        children = DataSourceDepartmentRelation.objects.get(
            department=tenant_department.data_source_department
        ).get_children()

        # 获取数据源部门基础信息
        data_source_department_info_map = DataSourceDepartmentHandler.get_department_info_map_by_ids(
            children.values_list("department_id", flat=True)
        )
        tenant_department_children = TenantDepartmentHandler.convert_data_source_department_to_tenant_department(
            tenant_department.tenant_id, data_source_department_info_map
        )
        data = [
            item.model_dump(include={"id", "name", "has_children"}) for item in tenant_department_children.values()
        ]
        return Response(TenantDepartmentChildrenListOutputSLZ(data, many=True).data)


class TenantUserListApi(CurrentUserTenantMixin, generics.ListAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
    serializer_class = TenantUserListOutputSLZ

    def get_tenant_user_ids(self, tenant_id):
        # 当前获取租户下所有用户
        current_tenant_id = self.get_current_tenant_id()
        if tenant_id != current_tenant_id:
            # FIXME 因协同数据源,绑定的租户用户
            return []

        return TenantUserHandler.get_tenant_user_ids_by_tenant(tenant_id=current_tenant_id)

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

        # 租户用户列表ids
        tenant_id = self.kwargs["id"]

        # build response
        queryset = self.filter_queryset(self.get_queryset().filter(id__in=self.get_tenant_user_ids(tenant_id)))
        if keyword := data.get("keyword"):
            queryset = queryset.select_related("data_source_user").filter(
                Q(data_source_user__username__icontains=keyword) | Q(data_source_user__full_name__icontains=keyword)
            )

        tenant_users = self.paginate_queryset(queryset)
        tenant_user_ids = [user.id for user in tenant_users]
        context = {
            "tenant_user_info_map": TenantUserHandler.list_tenant_user_by_id(tenant_user_ids),
            "tenant_user_departments_map": TenantUserHandler.get_tenant_user_departments_map_by_id(
                tenant_id, tenant_user_ids
            ),
        }
        serializer = TenantUserListOutputSLZ(tenant_users, many=True, context=context)
        return self.get_paginated_response(serializer.data)
