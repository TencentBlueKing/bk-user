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

from bkuser.apps.audit.constants import ObjectTypeEnum, OperationEnum
from bkuser.apps.audit.recorder import add_audit_record
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.models import TenantUser
from bkuser.apps.tenant.utils import TenantUserIDGenerator
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

    serializer_class = VirtualUserListOutputSLZ

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
        return queryset

    @swagger_auto_schema(
        tags=["virtual_user"],
        operation_description="虚拟用户列表",
        query_serializer=VirtualUserListInputSLZ(),
        responses={status.HTTP_200_OK: VirtualUserListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["virtual_user"],
        operation_description="新建虚拟用户",
        request_body=VirtualUserCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: VirtualUserCreateOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        data_source = self.get_current_virtual_data_source()
        slz = VirtualUserCreateInputSLZ(data=request.data, context={"data_source_id": data_source.id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        with transaction.atomic():
            # 创建数据源用户
            user = DataSourceUser.objects.create(
                data_source=data_source,
                code=data["username"],
                username=data["username"],
                full_name=data["full_name"],
                email=data["email"],
                phone=data["phone"],
                phone_country_code=data["phone_country_code"],
            )
            # 虚拟用户只会同步到数据源所属租户下
            tenant_id = data_source.owner_tenant_id
            tenant_user = TenantUser.objects.create(
                id=TenantUserIDGenerator(tenant_id, data_source).gen(user),
                data_source_user=user,
                tenant_id=tenant_id,
                data_source=data_source,
            )

        # 审计记录
        add_audit_record(
            operator=request.user.username,
            tenant_id=self.get_current_tenant_id(),
            operation=OperationEnum.CREATE_VIRTUAL_USER,
            object_type=ObjectTypeEnum.VIRTUAL_USER,
            object_id=tenant_user.id,
            extras={
                "name": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "phone_country_code": user.phone_country_code,
            },
        )

        return Response(status=status.HTTP_201_CREATED, data=VirtualUserCreateOutputSLZ(tenant_user).data)


class VirtualUserRetrieveUpdateDestroyApi(
    CurrentTenantVirtualDataSource, ExcludePatchAPIViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"
    serializer_class = VirtualUserRetrieveOutputSLZ

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
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["virtual_user"],
        operation_description="更新虚拟用户",
        request_body=VirtualUserUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        slz = VirtualUserUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 实际修改的字段属性都在关联的数据源用户上
        data_source_user = tenant_user.data_source_user

        name = data_source_user.username
        # 【审计】记录变更前的数据
        data_before = {
            "full_name": data_source_user.full_name,
            "email": data_source_user.email,
            "phone": data_source_user.phone,
            "phone_country_code": data_source_user.phone_country_code,
        }

        # 覆盖更新
        data_source_user.full_name = data["full_name"]
        data_source_user.email = data["email"]
        data_source_user.phone = data["phone"]
        data_source_user.phone_country_code = data["phone_country_code"]
        data_source_user.save(update_fields=["full_name", "email", "phone", "phone_country_code", "updated_at"])

        # 审计记录
        add_audit_record(
            operator=request.user.username,
            tenant_id=self.get_current_tenant_id(),
            operation=OperationEnum.MODIFY_VIRTUAL_USER,
            object_type=ObjectTypeEnum.VIRTUAL_USER,
            object_id=tenant_user.id,
            # 记录 name 方便前端展示
            extras={"data_before": data_before, "name": name},
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["virtual_user"],
        operation_description="删除虚拟用户",
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        data_source_user = tenant_user.data_source_user

        # 【审计】记录变更前的数据，删除后无法获取
        username = data_source_user.username
        full_name = data_source_user.full_name
        email = data_source_user.email
        phone = data_source_user.phone
        phone_country_code = data_source_user.phone_country_code

        with transaction.atomic():
            tenant_user.delete()
            data_source_user.delete()

        # 审计记录
        add_audit_record(
            operator=request.user.username,
            tenant_id=self.get_current_tenant_id(),
            operation=OperationEnum.DELETE_VIRTUAL_USER,
            object_type=ObjectTypeEnum.VIRTUAL_USER,
            object_id=tenant_user.id,
            extras={
                "name": username,
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "phone_country_code": phone_country_code,
            },
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
