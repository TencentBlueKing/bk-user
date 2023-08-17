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

from bkuser.apis.web.tenant_organization.serializers import (
    TenantsListOutputSLZ,
    TenantsRetrieveOutputSLZ,
    TenantUpdateInputSLZ,
)
from bkuser.apps.tenant.models import Tenant
from bkuser.biz.tenant import (
    TenantEditableBaseInfo,
    TenantFeatureFlag,
    TenantHandler,
)
from bkuser.common.views import ExcludePatchAPIViewMixin

logger = logging.getLogger(__name__)


class TenantsListApi(generics.ListAPIView):
    pagination_class = None
    queryset = Tenant.objects.all()
    serializer_class = TenantsListOutputSLZ

    def _get_tenant_id(self) -> str:
        # TODO 根据登录用户获取租户
        return self.queryset.first().id

    def get_serializer_context(self):
        return {"current_tenant_id": self._get_tenant_id()}

    def get_queryset(self):
        tenant_id = self._get_tenant_id()
        # TODO 协同数据源, 以租户的形式展示, 如何获取？
        return Tenant.objects.filter(id__in=[tenant_id])

    @swagger_auto_schema(
        operation_description="租户列表",
        responses={status.HTTP_200_OK: TenantsListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TenantRetrieveUpdateApi(ExcludePatchAPIViewMixin, generics.RetrieveUpdateAPIView):
    queryset = Tenant.objects.all()
    pagination_class = None
    serializer_class = TenantsRetrieveOutputSLZ
    lookup_url_kwarg = "id"

    def _get_tenant_id(self) -> str:
        # TODO 根据当前租户获取租户ID
        return self.queryset.first().id

    def get_serializer_context(self):
        # 根据当前登录的租户用户，获取租户ID
        tenant_id = self._get_tenant_id()
        # NOTE 因协同数据源，而展示的租户，不返回管理员
        return {
            "tenant_manager_map": TenantHandler.get_tenant_manager_map(tenant_ids=[tenant_id]),
        }

    @swagger_auto_schema(
        operation_description="单个租户详情",
        responses={status.HTTP_200_OK: TenantsRetrieveOutputSLZ()},
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
        # NOTE 因协同数据源，而展示的租户，不返回管理员
        if self._get_tenant_id() != instance.id:
            return Response

        should_updated_info = TenantEditableBaseInfo(
            name=data["name"], logo=data.get("logo") or "", feature_flags=TenantFeatureFlag(**data["feature_flags"])
        )

        TenantHandler.update_with_managers(instance.id, should_updated_info, data["manager_ids"])

        return Response()
