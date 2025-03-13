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
from django.db.models import QuerySet
from rest_framework import generics
from rest_framework.response import Response

from bkuser.apps.tenant.models import TenantUser

from .mixins import InnerApiCommonMixin
from .serializers import TenantUserContactInfoListInputSLZ, TenantUserContactInfoListOutputSLZ


class TenantUserRetrieveApi(InnerApiCommonMixin, generics.RetrieveAPIView):
    """
    查询用户信息
    Note: 网关内部接口对性能要求较高，所以不进行序列化，且查询必须按字段
    TODO：后续根据耗时统计进行 Cache 优化
    """

    # [only] 用于减少查询字段，仅查询必要字段
    queryset = TenantUser.objects.all().only("tenant_id")
    lookup_url_kwarg = "id"

    def get(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        return Response({"tenant_id": tenant_user.tenant_id})


class TenantUserContactInfoListApi(InnerApiCommonMixin, generics.ListAPIView):
    """
    根据 bk_username 批量查询用户联系方式
    """

    pagination_class = None

    serializer_class = TenantUserContactInfoListOutputSLZ

    def get_queryset(self) -> QuerySet[TenantUser]:
        slz = TenantUserContactInfoListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        return TenantUser.objects.filter(id__in=data["bk_usernames"], tenant_id=self.tenant_id).select_related(
            "data_source_user"
        )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
