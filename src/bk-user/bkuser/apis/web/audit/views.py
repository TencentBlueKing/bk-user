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
from datetime import timedelta
from typing import Any, Dict

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.audit.models import OperationAuditRecord
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.biz.tenant import TenantUserHandler

from .serializers import AuditRecordListInputSLZ, AuditRecordListOutputSLZ


class AuditRecordListAPIView(CurrentUserTenantMixin, generics.ListAPIView):
    """操作审计记录列表"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    serializer_class = AuditRecordListOutputSLZ

    def get_queryset(self):
        slz = AuditRecordListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        filters = {
            "tenant_id": self.get_current_tenant_id(),
        }

        if creator := params.get("creator"):
            filters["creator"] = creator

        if operation := params.get("operation"):
            filters["operation"] = operation

        if object_type := params.get("object_type"):
            filters["object_type"] = object_type

        if created_at := params.get("created_at"):
            filters["created_at__gte"] = created_at
            filters["created_at__lt"] = created_at + timedelta(seconds=1)

        if object_name := params.get("object_name"):
            filters["object_name__icontains"] = object_name

        return OperationAuditRecord.objects.filter(**filters)

    def get_serializer_context(self) -> Dict[str, Any]:
        queryset = self.paginate_queryset(self.get_queryset())
        tenant_user_ids = [record.creator for record in queryset]
        return {
            "user_display_name_map": TenantUserHandler.get_tenant_user_display_name_map_by_ids(tenant_user_ids),
        }

    @swagger_auto_schema(
        tags=["audit"],
        operation_description="操作审计列表",
        query_serializer=AuditRecordListInputSLZ(),
        responses={status.HTTP_200_OK: AuditRecordListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
