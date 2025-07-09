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

from django.db import transaction
from django.db.models import Q, QuerySet
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.auditor import VirtualUserAuditor
from bkuser.biz.virtual_user import VirtualUserHandler
from bkuser.common.views import ExcludePatchAPIViewMixin

from .mixins import CurrentTenantVirtualDataSource
from .serializers import (
    VirtualUserCreateInputSLZ,
    VirtualUserCreateOutputSLZ,
    VirtualUserListInputSLZ,
    VirtualUserListOutputSLZ,
    VirtualUserRetrieveOutputSLZ,
    VirtualUserUpdateInputSLZ,
)


class VirtualUserListCreateApi(CurrentTenantVirtualDataSource, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    def get_queryset(self) -> QuerySet[TenantUser]:
        slz = VirtualUserListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 过滤当前租户的虚拟用户
        queryset = TenantUser.objects.filter(
            tenant_id=self.get_current_tenant_id(), data_source__type=DataSourceTypeEnum.VIRTUAL
        ).select_related("data_source_user")

        # 关键字过滤
        if keyword := data.get("keyword"):
            queryset = queryset.filter(
                Q(data_source_user__username__icontains=keyword) | Q(data_source_user__full_name__icontains=keyword)
            )

        # TODO: 后续需要支持排序
        # 默认先按照时间倒序排列
        return queryset.order_by("-created_at")

    @swagger_auto_schema(
        tags=["virtual_user"],
        operation_description="虚拟用户列表",
        query_serializer=VirtualUserListInputSLZ(),
        responses={status.HTTP_200_OK: VirtualUserListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        detailed_vusers = VirtualUserHandler.to_detailed_virtual_users(page)
        return self.get_paginated_response(VirtualUserListOutputSLZ(detailed_vusers, many=True).data)

    @swagger_auto_schema(
        tags=["virtual_user"],
        operation_description="新建虚拟用户",
        request_body=VirtualUserCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: VirtualUserCreateOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        data_source = self.get_current_virtual_data_source()
        cur_tenant_id = self.get_current_tenant_id()

        slz = VirtualUserCreateInputSLZ(
            data=request.data, context={"data_source_id": data_source.id, "tenant_id": cur_tenant_id}
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        with transaction.atomic():
            # 创建虚拟用户
            tenant_user = VirtualUserHandler.create(
                data_source=data_source,
                username=data["username"],
                full_name=data["full_name"],
            )

            # 创建虚拟用户与应用的关联
            VirtualUserHandler.add_app_codes(tenant_user, data["app_codes"])
            # 创建虚拟用户与责任人的关联
            VirtualUserHandler.add_owners(tenant_user, data["owners"])

        # 【审计】创建虚拟用户审计对象
        auditor = VirtualUserAuditor(request.user.username, cur_tenant_id)
        # 【审计】将审计记录保存至数据库
        auditor.record_create(tenant_user)

        return Response(status=status.HTTP_201_CREATED, data=VirtualUserCreateOutputSLZ(tenant_user).data)


class VirtualUserRetrieveUpdateApi(
    CurrentTenantVirtualDataSource, ExcludePatchAPIViewMixin, generics.RetrieveUpdateAPIView
):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[TenantUser]:
        # 过滤当前租户的虚拟用户
        return TenantUser.objects.filter(
            tenant_id=self.get_current_tenant_id(), data_source__type=DataSourceTypeEnum.VIRTUAL
        )

    @swagger_auto_schema(
        tags=["virtual_user"],
        operation_description="虚拟用户详情",
        responses={status.HTTP_200_OK: VirtualUserRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        virtual_user = self.get_object()
        detailed_vuser = VirtualUserHandler.to_detailed_virtual_users([virtual_user])[0]
        return Response(VirtualUserRetrieveOutputSLZ(detailed_vuser).data)

    @swagger_auto_schema(
        tags=["virtual_user"],
        operation_description="更新虚拟用户",
        request_body=VirtualUserUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        cur_tenant_id = self.get_current_tenant_id()

        slz = VirtualUserUpdateInputSLZ(data=request.data, context={"tenant_id": cur_tenant_id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 【审计】创建虚拟用户审计对象并记录变更前的数据
        auditor = VirtualUserAuditor(request.user.username, cur_tenant_id)
        auditor.pre_record_data_before(tenant_user)

        data_source_user = tenant_user.data_source_user

        with transaction.atomic():
            # 覆盖更新
            data_source_user.full_name = data["full_name"]
            data_source_user.save(update_fields=["full_name", "updated_at"])

            # 更新虚拟用户与应用的关联
            VirtualUserHandler.update_app_codes(tenant_user, data["app_codes"])
            # 更新虚拟用户与责任人的关联
            VirtualUserHandler.update_owners(tenant_user, data["owners"])

        # 【审计】将审计记录保存至数据库
        auditor.record_update(tenant_user)

        return Response(status=status.HTTP_204_NO_CONTENT)
