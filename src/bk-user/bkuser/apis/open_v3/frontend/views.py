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

from bkuser.apis.open_v3.frontend.mixins import FrontApiCommonMixin
from bkuser.apis.open_v3.frontend.serializers import (
    TenantUserDisplayNameListInputSLZ,
    TenantUserDisplayNameListOutputSLZ,
    TenantUserDisplayNameRetrieveOutputSLZ,
)
from bkuser.apps.tenant.models import TenantUser


class TenantUserDisplayNameRetrieveApi(FrontApiCommonMixin, generics.RetrieveAPIView):
    """
    查询用户展示名
    Note: 前端服务专用 API 接口
    """

    lookup_url_kwarg = "id"
    serializer_class = TenantUserDisplayNameRetrieveOutputSLZ

    def get_queryset(self):
        # TODO: 由于目前 DisplayName 渲染只与 full_name 相关，所以只查询 full_name
        # 后续支持表达式，则需要查询表达式可配置的所有字段
        return (
            TenantUser.objects.filter(
                tenant_id=self.tenant_id,
                data_source_id=self.real_data_source_id,
            )
            .select_related("data_source_user")
            .only("data_source_user__full_name")
        )

    @swagger_auto_schema(
        tags=["open_v3.frontend.user"],
        operation_id="retrieve_user_display_name",
        operation_description="查询用户展示名",
        responses={status.HTTP_200_OK: TenantUserDisplayNameRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class TenantUserDisplayNameListApi(FrontApiCommonMixin, generics.ListAPIView):
    """
    批量查询用户展示名
    Note: 前端服务专用 API 接口
    """

    pagination_class = None

    serializer_class = TenantUserDisplayNameListOutputSLZ

    def get_queryset(self):
        slz = TenantUserDisplayNameListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # TODO: 由于目前 DisplayName 渲染只与 full_name 相关，所以只查询 full_name
        # 后续支持表达式，则需要查询表达式可配置的所有字段
        return (
            TenantUser.objects.filter(
                id__in=data["bk_usernames"],
                tenant_id=self.tenant_id,
                data_source_id=self.real_data_source_id,
            )
            .select_related("data_source_user")
            .only("id", "data_source_user__full_name")
        )

    @swagger_auto_schema(
        tags=["open_v3.frontend.user"],
        operation_id="batch_query_user_display_name",
        operation_description="批量查询用户展示名",
        query_serializer=TenantUserDisplayNameListInputSLZ(),
        responses={status.HTTP_200_OK: TenantUserDisplayNameListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
