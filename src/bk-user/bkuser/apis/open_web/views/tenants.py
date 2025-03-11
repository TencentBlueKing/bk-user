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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apis.open_web.mixins import OpenWebApiCommonMixin
from bkuser.apis.open_web.serializers.tenants import TenantRetrieveOutputSLZ
from bkuser.apps.tenant.constants import CollaborationStrategyStatus
from bkuser.apps.tenant.models import CollaborationStrategy, Tenant


class TenantRetrieveApi(OpenWebApiCommonMixin, generics.ListAPIView):
    """获取租户信息(包括协同)"""

    @swagger_auto_schema(
        tags=["open_web.tenant"],
        operation_id="open_web.tenant.retrieve",
        operation_description="获取租户信息",
        responses={status.HTTP_200_OK: TenantRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant = Tenant.objects.get(id=self.tenant_id)

        collaboration_tenant_ids = (
            CollaborationStrategy.objects.filter(target_tenant_id=self.tenant_id)
            .exclude(target_status=CollaborationStrategyStatus.UNCONFIRMED)
            .values_list("source_tenant_id", flat=True)
        )

        collab_tenants = Tenant.objects.filter(id__in=collaboration_tenant_ids)

        info = {
            "id": tenant.id,
            "name": tenant.name,
            "collab_tenants": [{"id": d.id, "name": d.name} for d in collab_tenants],
        }

        return Response(TenantRetrieveOutputSLZ(info).data)
