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

from typing import Any, Dict

from django.conf import settings
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apis.open_web.mixins import OpenWebApiCommonMixin
from bkuser.apis.open_web.serializers.users import (
    TenantUserDisplayInfoListInputSLZ,
    TenantUserDisplayInfoListOutputSLZ,
    TenantUserDisplayInfoRetrieveOutputSLZ,
    TenantUserSearchInputSLZ,
    TenantUserSearchOutputSLZ,
)
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.tenant.models import Tenant, TenantUser
from bkuser.biz.tenant import TenantUserHandler


class TenantUserDisplayInfoRetrieveApi(OpenWebApiCommonMixin, generics.RetrieveAPIView):
    """
    查询用户展示信息
    Note: 前端服务专用 API 接口，该接口对性能要求较高，所以不进行序列化，且查询必须按字段
    """

    @swagger_auto_schema(
        tags=["open_web.user"],
        operation_id="retrieve_user_display_info",
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


class TenantUserSearchApi(OpenWebApiCommonMixin, generics.ListAPIView):
    """
    搜索用户（包括协同用户与虚拟用户）
    """

    pagination_class = None

    serializer_class = TenantUserSearchOutputSLZ

    # 限制搜索结果，只提供前 N 条记录，如果展示不完全，需要用户细化搜索条件
    search_limit = settings.SELECTOR_SEARCH_API_LIMIT

    def get_queryset(self) -> QuerySet[TenantUser]:
        slz = TenantUserSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        filters: Dict[str, Any] = {
            "tenant_id": self.tenant_id,
        }

        # 如果不开启协同租户用户搜索，则只搜索当前租户用户
        if not settings.ENABLE_DISPLAY_COLLABORATION_TENANT:
            filters["data_source__owner_tenant_id"] = self.tenant_id

        # 如果不开启虚拟用户搜索，则只搜索实名用户
        if not settings.ENABLE_DISPLAY_VIRTUAL_USER:
            filters["data_source_id"] = self.real_data_source_id

        queryset = (
            TenantUser.objects.filter(**filters)
            .exclude(data_source__type=DataSourceTypeEnum.BUILTIN_MANAGEMENT)
            .select_related("data_source_user", "data_source")
            .only("id", "data_source_user__username", "data_source_user__full_name", "data_source__owner_tenant_id")
        )

        if keyword := data.get("keyword"):
            # TODO: 后续支持更多搜索条件（例如 phone、email 等）
            queryset = queryset.filter(
                Q(data_source_user__username__icontains=keyword) | Q(data_source_user__full_name__icontains=keyword)
            )

        return queryset[: self.search_limit]

    @swagger_auto_schema(
        tags=["open_web.user"],
        operation_id="search_user",
        operation_description="搜索用户",
        query_serializer=TenantUserSearchInputSLZ(),
        responses={status.HTTP_200_OK: TenantUserSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        tenant_depts = self.get_queryset()
        # 只有协同租户用户需要提供原始租户 ID 与 租户名称
        collab_tenant_ids = set(tenant_depts.values_list("data_source__owner_tenant_id", flat=True)) - {self.tenant_id}
        context = {
            "collab_user_tenant_name_map": dict(
                Tenant.objects.filter(id__in=collab_tenant_ids).values_list("id", "name")
            )
        }
        return Response(TenantUserSearchOutputSLZ(tenant_depts, many=True, context=context).data)
