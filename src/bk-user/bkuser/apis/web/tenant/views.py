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

from rest_framework import generics
from rest_framework.response import Response

from bkuser.apis.web.tenant.serializers import (
    TenantUpdateInputSLZ,
    TenantUpdateOutputSLZ
)
from bkuser.apps.tenant.models import Tenant
from bkuser.biz.tenant_handler import tenant_handler

logger = logging.getLogger(__name__)


class TenantRetrieveUpdateApi(generics.RetrieveUpdateAPIView):
    queryset = Tenant.objects.filter()
    serializer_class = TenantUpdateOutputSLZ

    def put(self, request, *args, **kwargs):
        slz = TenantUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        instance = self.get_object()
        tenant_handler.update_tenant(instance, data)

        new_manager_ids = data["manager_ids"]
        tenant_handler.update_tenant_managers(instance.id, new_manager_ids)
        return Response(data=TenantUpdateOutputSLZ(instance=instance).data)
