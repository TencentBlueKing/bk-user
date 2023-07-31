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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apis.web.tenant.serializers import (
    TenantCreateInputSlZ,
    TenantCreateOutputSLZ,
    TenantDetailSLZ,
    TenantOutputSLZ,
    TenantSearchSLZ,
    TenantUpdateInputSLZ,
    TenantUpdateOutputSLZ,
    TenantUsersSLZ,
)
from bkuser.apps.tenant.models import Tenant, TenantUser
from bkuser.biz.tenant_handler import tenant_handler

logger = logging.getLogger(__name__)


class TenantListCreateApi(generics.ListCreateAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantOutputSLZ
    pagination_class = None

    def list(self, request, *args, **kwargs):
        slz = TenantSearchSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        name = slz.data.get("name")
        if name:
            self.queryset = Tenant.objects.filter(name__icontains=name)

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=TenantCreateInputSlZ(),
        responses={status.HTTP_200_OK: TenantCreateOutputSLZ()},
        tags=["tenants"],
    )
    def post(self, request, *args, **kwargs):
        slz = TenantCreateInputSlZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 初始化租户和租户管理员
        tenant = tenant_handler.init_tenant_with_managers(data)

        return Response(data=TenantCreateOutputSLZ(instance=tenant).data)


class TenantRetrieveUpdateApi(generics.RetrieveUpdateAPIView):
    queryset = Tenant.objects.all()
    lookup_url_kwarg = "id"
    serializer_class = TenantDetailSLZ

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.queryset)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=TenantUpdateInputSLZ(),
        responses={status.HTTP_200_OK: TenantUpdateOutputSLZ()},
        tags=["tenants"],
    )
    def put(self, request, *args, **kwargs):
        slz = TenantUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        instance = self.get_object()
        tenant_handler.update_tenant(instance, data)

        new_manager_ids = data["manager_ids"]
        tenant_handler.update_tenant_managers(instance.id, new_manager_ids)
        return Response(data=TenantUpdateOutputSLZ(instance=instance).data)


class TenantUsersListApi(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        tenant_id = kwargs["tenant_id"]
        tenant_users = TenantUser.objects.filter(tenant_id=tenant_id)
        serializer = TenantUsersSLZ(tenant_users, many=True)

        return Response(serializer.data)
