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

from bkuser.apis.web.organization.serializers import TenantDepartmentChildrenListOutputSLZ
from bkuser.biz.tenant import TenantDepartmentHandler

logger = logging.getLogger(__name__)


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
        return Response(self.get_serializer(data, many=True).data)
