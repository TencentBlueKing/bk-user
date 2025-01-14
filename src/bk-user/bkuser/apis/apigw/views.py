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
from bkuser.common.error_codes import error_codes

from .mixins import InnerApiCommonMixin
from .serializers import TenantUserListInputSLZ, TenantUserListOutputSLZ


class TenantUserRetrieveApi(InnerApiCommonMixin, generics.RetrieveAPIView):
    """
    查询用户信息
    Note: 网关内部接口对性能要求较高，所以不进行序列化，且查询必须按字段
    TODO：后续根据耗时统计进行 Cache 优化
    """

    def get(self, request, *args, **kwargs):
        tenant_user_id = kwargs["tenant_user_id"]

        # [only] 用于减少查询字段，仅查询必要字段
        tenant_user = TenantUser.objects.filter(id=tenant_user_id).only("tenant_id").first()
        if not tenant_user:
            raise error_codes.OBJECT_NOT_FOUND.f(f"user({tenant_user_id}) not found", replace=True)

        return Response({"tenant_id": tenant_user.tenant_id})


class TenantUserContactInfoListApi(InnerApiCommonMixin, generics.ListAPIView):
    """
    根据 bk_username 批量查询用户联系方式
    """

    pagination_class = None

    serializer_class = TenantUserListOutputSLZ

    def get_queryset(self) -> QuerySet[TenantUser]:
        # 从 Header 中获取当前租户 ID
        cur_tenant_id = self.request.META.get("HTTP_X_BK_TENANT_ID")
        if not cur_tenant_id:
            raise error_codes.INVALID_ARGUMENT.f("X-Bk-Tenant-Id header is required", replace=True)

        slz = TenantUserListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # [only] 用于减少查询字段，仅查询必要字段
        return (
            TenantUser.objects.filter(id__in=data["bk_usernames"], tenant_id=cur_tenant_id)
            .select_related("data_source_user")
            .only(
                "id",
                "tenant_id",
                "data_source_user__full_name",
                "data_source_user__phone_country_code",
                "data_source_user__phone",
                "data_source_user__email",
            )
        )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
