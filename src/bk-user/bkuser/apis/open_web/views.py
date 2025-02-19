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

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apis.open_web.mixins import OpenWebApiCommonMixin
from bkuser.apis.open_web.serializers import (
    TenantUserDisplayInfoListInputSLZ,
    TenantUserDisplayInfoListOutputSLZ,
    TenantUserDisplayInfoRetrieveOutputSLZ,
)
from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.tenant import TenantUserHandler


class TenantUserDisplayInfoRetrieveApi(OpenWebApiCommonMixin, generics.RetrieveAPIView):
    """
    查询用户展示信息
    Note: 前端服务专用 API 接口，该接口对性能要求较高，所以不进行序列化，且查询必须按字段
    """

    @swagger_auto_schema(
        tags=["open_web.user"],
        operation_id="query_user_display_info",
        operation_description="查询用户展示信息",
        responses={status.HTTP_200_OK: TenantUserDisplayInfoRetrieveOutputSLZ()},
    )
    @method_decorator(cache_control(public=True, max_age=60 * 5))
    def get(self, request, *args, **kwargs):
        # TODO: 由于目前 DisplayName 渲染只与 full_name 相关，所以只查询 full_name
        # 后续支持表达式，则需要查询表达式可配置的所有字段
        tenant_user = get_object_or_404(
            TenantUser.objects.filter(
                tenant_id=self.tenant_id,
                data_source_id=self.real_data_source_id,
            )
            .select_related("data_source_user")
            .only("data_source_user__full_name"),
            id=kwargs["id"],
        )

        return Response({"display_name": TenantUserHandler.generate_tenant_user_display_name(tenant_user)})


class TenantUserDisplayInfoListApi(OpenWebApiCommonMixin, generics.ListAPIView):
    """
    批量查询用户展示信息
    Note: 前端服务专用 API 接口
    """

    pagination_class = None

    serializer_class = TenantUserDisplayInfoListOutputSLZ

    def get_queryset(self):
        slz = TenantUserDisplayInfoListInputSLZ(data=self.request.query_params)
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
        tags=["open_web.user"],
        operation_id="batch_query_user_display_info",
        operation_description="批量查询用户展示信息",
        query_serializer=TenantUserDisplayInfoListInputSLZ(),
        responses={status.HTTP_200_OK: TenantUserDisplayInfoListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
