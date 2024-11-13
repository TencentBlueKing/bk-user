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

from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from bkuser.apps.audit.constants import ObjectTypeEnum, OperationEnum
from bkuser.apps.audit.models import OperationAuditRecord
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class

from .serializers import OperationAuditRecordListInputSerializer, OperationAuditRecordListOutputSerializer


class AuditRecordListAPIView(generics.ListAPIView):
    """操作审计记录列表"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    serializer_class = OperationAuditRecordListOutputSerializer

    def get_queryset(self):
        slz = OperationAuditRecordListInputSerializer(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        filters = Q()
        if params.get("operator"):
            filters &= Q(creator=params["operator"])
        if params.get("operation"):
            filters &= Q(operation=params["operation"])
        if params.get("object_type"):
            filters &= Q(object_type=params["object_type"])
        if params.get("created_at"):
            start_time = params["created_at"].replace(microsecond=0)
            end_time = params["created_at"].replace(microsecond=999999)
            filters &= Q(created_at__range=(start_time, end_time))
        if params.get("object_name"):
            filters &= Q(object_name__icontains=params["object_name"])

        return OperationAuditRecord.objects.filter(filters)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["operation_map"] = dict(OperationEnum.get_choices())
        context["object_type_map"] = dict(ObjectTypeEnum.get_choices())
        return context

    @swagger_auto_schema(
        tags=["audit"],
        operation_description="操作审计列表",
        query_serializer=OperationAuditRecordListInputSerializer(),
        responses={status.HTTP_200_OK: OperationAuditRecordListOutputSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
