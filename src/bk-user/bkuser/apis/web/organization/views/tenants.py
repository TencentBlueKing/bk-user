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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apis.web.organization.serializers import (
    TenantListOutputSLZ,
    TenantRetrieveOutputSLZ,
)
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.models import Tenant, TenantDepartment, TenantUser


class CurrentTenantRetrieveApi(CurrentUserTenantMixin, generics.RetrieveAPIView):
    """获取当前用户所在租户信息"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["organization"],
        operation_description="获取当前用户所在租户信息",
        responses={status.HTTP_200_OK: TenantRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant = Tenant.objects.get(id=self.get_current_tenant_id())
        return Response(TenantRetrieveOutputSLZ(tenant).data, status=status.HTTP_200_OK)


class CollaborativeTenantListApi(CurrentUserTenantMixin, generics.ListAPIView):
    """获取当前租户的协作租户信息"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    pagination_class = None
    serializer_class = TenantListOutputSLZ

    def get_queryset(self):
        # TODO (su) 目前是根据部门信息获取的协作租户 ID，后续可修改成根据协同策略获取？
        # 不过通过部门反查优点是一定有数据（协作策略已确认，但是未同步的情况）
        cur_tenant_id = self.get_current_tenant_id()
        dept_tenant_ids = (
            TenantDepartment.objects.filter(tenant_id=cur_tenant_id)
            .exclude(data_source__owner_tenant_id=cur_tenant_id)
            .distinct()
        )
        user_tenant_ids = (
            TenantUser.objects.filter(tenant_id=cur_tenant_id)
            .exclude(data_source__owner_tenant_id=cur_tenant_id)
            .distinct()
        )
        # 需要用户和部门的 owner_tenant_id 取并集，避免出现用户不属于任何部门的情况
        collaborative_tenant_ids = set(dept_tenant_ids) | set(user_tenant_ids)
        return Tenant.objects.filter(id__in=collaborative_tenant_ids)

    @swagger_auto_schema(
        tags=["organization"],
        operation_description="获取当前租户的协作租户信息",
        responses={status.HTTP_200_OK: TenantListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
