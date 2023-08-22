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

from bkuser.apis.web.organization.serializers import TenantListOutputSLZ
from bkuser.apis.web.tenant.serializers import TenantRetrieveOutputSLZ, TenantUpdateInputSLZ
from bkuser.apps.tenant.models import Tenant
from bkuser.biz.tenant import (
    TenantDepartmentHandler,
    TenantEditableBaseInfo,
    TenantFeatureFlag,
    TenantHandler,
)
from bkuser.common.error_codes import error_codes
from bkuser.common.views import ExcludePatchAPIViewMixin

logger = logging.getLogger(__name__)


class TenantListApi(generics.ListAPIView):
    pagination_class = None
    queryset = Tenant.objects.all()
    serializer_class = TenantListOutputSLZ

    def _get_tenant_id(self) -> str:
        return self.request.user.get_property("tenant_id")

    def get_serializer_context(self):
        tenant_ids = list(self.queryset.values_list("id", flat=True))
        tenant_root_departments_map = TenantDepartmentHandler.get_tenant_root_departments_by_id(
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
        return {"current_tenant_id": self._get_tenant_id()}

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
