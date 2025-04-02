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
import logging

from django.db.models import QuerySet
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status

from bkuser.apis.open_v3.mixins import OpenApiCommonMixin
from bkuser.apis.open_v3.serializers.tenant import (
    TenantListOutputSLZ,
    TenantPropertyListOutputSLZ,
    TenantPropertyLookupInputSLZ,
    TenantPropertyLookupOutputSLZ,
)
from bkuser.apps.tenant.models import Tenant, TenantProperty

logger = logging.getLogger(__name__)


class TenantListApi(OpenApiCommonMixin, generics.ListAPIView):
    pagination_class = None
    serializer_class = TenantListOutputSLZ
    queryset = Tenant.objects.all()

    @swagger_auto_schema(
        tags=["open_v3.tenant"],
        operation_id="list_tenant",
        operation_description="获取租户列表",
        responses={status.HTTP_200_OK: TenantListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TenantPropertyListApi(OpenApiCommonMixin, generics.ListAPIView):
    """
    获取租户的公共属性
    """

    serializer_class = TenantPropertyListOutputSLZ

    def get_queryset(self) -> QuerySet[TenantProperty]:
        return TenantProperty.objects.filter(tenant_id=self.tenant_id)

    @swagger_auto_schema(
        tags=["open_v3.tenant"],
        operation_id="list_tenant_property.md",
        operation_description="获取租户的公共属性",
        responses={status.HTTP_200_OK: TenantPropertyListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TenantPropertyLookupApi(OpenApiCommonMixin, generics.ListAPIView):
    """
    批量查询租户公共属性
    """

    pagination_class = None

    serializer_class = TenantPropertyLookupOutputSLZ

    def get_queryset(self) -> QuerySet[TenantProperty]:
        slz = TenantPropertyLookupInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        return TenantProperty.objects.filter(tenant_id=self.tenant_id, key__in=data["lookups"])

    @swagger_auto_schema(
        tags=["open_v3.tenant"],
        operation_id="batch_lookup_tenant_property",
        operation_description="批量查询租户的公共属性",
        query_serializer=TenantPropertyLookupInputSLZ(),
        responses={status.HTTP_200_OK: TenantPropertyLookupOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
