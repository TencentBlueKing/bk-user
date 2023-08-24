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
from rest_framework.response import Response

from bkuser.apis.web.organization.serializers import (
    TenantDepartmentChildrenListOutputSLZ,
    TenantDepartmentUserListOutputSLZ,
    TenantDepartmentUserSearchInputSLZ,
    TenantListOutputSLZ,
    TenantUserRetrieveOutputSLZ,
)
from bkuser.apis.web.tenant.serializers import TenantRetrieveOutputSLZ, TenantUpdateInputSLZ
from bkuser.apps.tenant.models import Tenant, TenantUser
from bkuser.biz.tenant import (
    TenantDepartmentHandler,
    TenantEditableBaseInfo,
    TenantFeatureFlag,
    TenantHandler,
    TenantUserHandler,
)
from bkuser.common.error_codes import error_codes
from bkuser.common.pagination import CustomPageNumberPagination
from bkuser.common.views import ExcludePatchAPIViewMixin

logger = logging.getLogger(__name__)


class TenantDepartmentUserListApi(generics.ListAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    pagination_class = CustomPageNumberPagination
    serializer_class = TenantDepartmentUserListOutputSLZ

    def get_serializer_context(self):
        # 过滤出该租户部门(包括子部门)的租户用户
        tenant_user_ids = TenantUserHandler.get_tenant_user_ids_by_tenant_department(
            tenant_department_id=self.kwargs["id"], recursive=self.request.query_params.get("recursive", True)
        )

        # 租户用户基础信息
        tenant_users = TenantUserHandler.list_tenant_user_by_id(tenant_user_ids)
        tenant_users_info_map = {i.id: i for i in tenant_users}

        # 租户用户所属租户组织
        tenant_user_departments_map = TenantUserHandler.get_tenant_user_departments_map_by_id(tenant_user_ids)

        # 租户用户上级信息
        tenant_user_leaders_map = TenantUserHandler.get_tenant_user_leaders_map_by_id(tenant_user_ids)
        return {
            "tenant_users_info": tenant_users_info_map,
            "tenant_user_departments": tenant_user_departments_map,
            "tenant_user_leaders": tenant_user_leaders_map,
        }

    @swagger_auto_schema(
        operation_description="租户部门下用户详情列表",
        responses={status.HTTP_200_OK: TenantDepartmentUserListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        slz = TenantDepartmentUserSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        # 过滤该租户部门下的用户
        tenant_user_ids = TenantUserHandler.get_tenant_user_ids_by_tenant_department(
            tenant_department_id=self.kwargs["id"], recursive=data.get("recursive")
        )

        # build response
        queryset = self.filter_queryset(self.get_queryset().filter(id__in=tenant_user_ids))
        if keyword := data.get("keyword"):
            queryset = queryset.select_related("data_source_user").filter(
                Q(data_source_user__username__icontains=keyword)
                | Q(data_source_user__email__icontains=keyword)
                | Q(data_source_user__phone__icontains=keyword),
            )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TenantUsersRetrieveApi(generics.RetrieveAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    serializer_class = TenantUserRetrieveOutputSLZ

    @swagger_auto_schema(
        operation_description="租户部门下单个用户详情",
        responses={status.HTTP_200_OK: TenantUserRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class TenantListApi(generics.ListAPIView):
    pagination_class = None
    queryset = Tenant.objects.all()
    serializer_class = TenantListOutputSLZ

    def _get_tenant_id(self) -> str:
        return self.request.user.get_property("tenant_id")

    def get_serializer_context(self):
        tenant_ids = list(self.queryset.values_list("id", flat=True))
        tenant_root_departments_map = TenantDepartmentHandler.get_tenant_root_department_map_by_tenant_id(
            tenant_ids, self._get_tenant_id()
        )
        return {"tenant_root_departments_map": tenant_root_departments_map}

    @swagger_auto_schema(
        operation_description="租户列表",
        responses={status.HTTP_200_OK: TenantListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TenantRetrieveUpdateApi(ExcludePatchAPIViewMixin, generics.RetrieveUpdateAPIView):
    queryset = Tenant.objects.all()
    pagination_class = None
    serializer_class = TenantRetrieveOutputSLZ
    lookup_url_kwarg = "id"

    def _get_tenant_id(self) -> str:
        return self.request.user.get_property("tenant_id")

    def get_serializer_context(self):
        current_tenant_id = self._get_tenant_id()
        return {"tenant_manager_map": {current_tenant_id: TenantHandler.retrieve_tenant_managers(current_tenant_id)}}

    @swagger_auto_schema(
        operation_description="单个租户详情",
        responses={status.HTTP_200_OK: TenantRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="更新租户",
        request_body=TenantUpdateInputSLZ(),
        responses={status.HTTP_200_OK: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = TenantUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        instance = self.get_object()
        # NOTE 因协同数据源而展示的租户，非当前租户, 无权限做更新操作
        if self._get_tenant_id() != instance.id:
            raise error_codes.NO_PERMISSION

        should_updated_info = TenantEditableBaseInfo(
            name=data["name"], logo=data["logo"] or "", feature_flags=TenantFeatureFlag(**data["feature_flags"])
        )

        TenantHandler.update_with_managers(instance.id, should_updated_info, data["manager_ids"])
        return Response()


class TenantDepartmentChildrenListApi(generics.ListAPIView):
    pagination_class = None
    serializer_class = TenantDepartmentChildrenListOutputSLZ

    @swagger_auto_schema(
        operation_description="租户部门的二级子部门列表",
        responses={status.HTTP_200_OK: TenantDepartmentChildrenListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        tenant_department_id = self.kwargs["id"]
        # 拉取子部门信息列表
        tenant_department_children = TenantDepartmentHandler.get_tenant_department_children_by_id(tenant_department_id)
        data = [item.model_dump(include={"id", "name", "has_children"}) for item in tenant_department_children]
        return Response(TenantDepartmentChildrenListOutputSLZ(data, many=True).data)
