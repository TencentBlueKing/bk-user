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
from bkuser.apis.web.tenant.filters import TenantFilter
from bkuser.apis.web.tenant.serializers import TenantOutputSLZ, TenantSearchSLZ
from bkuser.apps.tenant.models import Tenant
from rest_framework import generics
from rest_framework.response import Response


class TenantListCreateApi(generics.ListCreateAPIView):
    queryset = Tenant.objects.filter()
    serializer_class = TenantOutputSLZ
    filter_backends = [TenantFilter]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        slz = TenantSearchSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
