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
import operator
from functools import reduce
from typing import List

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
    TenantUserLookupInputSLZ,
    TenantUserLookupOutputSLZ,
    TenantUserSearchInputSLZ,
    TenantUserSearchOutputSLZ,
)
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.tenant.models import TenantUser
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
        # 后续支持表达式，则需要查询表达式可配置的所有字段
        tenant_user = get_object_or_404(
            TenantUser.objects.filter(
                tenant_id=self.tenant_id,
                data_source_id=self.real_data_source_id,
            )
            .select_related("data_source_user")
            .only("data_source_user__username", "data_source_user__full_name"),
            id=kwargs["id"],
        )

        return Response(
            {
                "login_name": tenant_user.data_source_user.username,
                "full_name": tenant_user.data_source_user.full_name,
                "display_name": TenantUserHandler.generate_tenant_user_display_name(tenant_user),
            }
        )


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

        # 后续支持表达式，则需要查询表达式可配置的所有字段
        return (
            TenantUser.objects.filter(
                id__in=data["bk_usernames"],
                tenant_id=self.tenant_id,
                data_source_id=self.real_data_source_id,
            )
            .select_related("data_source_user")
            .only("id", "data_source_user__username", "data_source_user__full_name")
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

        keyword = data["keyword"]
        # TODO: 后续支持更多搜索条件（例如 phone、email 等）
        filter_args = [
            Q(tenant_id=self.tenant_id),
            Q(data_source_user__username__icontains=keyword) | Q(data_source_user__full_name__icontains=keyword),
        ]

        # 若指定了数据源类型，则只搜索该类型的用户；否则搜索所有数据源类型（除内置管理）的用户
        if data_source_type := data.get("data_source_type"):
            filter_args.append(Q(data_source__type=data_source_type))
        else:
            filter_args.append(Q(data_source__type__in=[DataSourceTypeEnum.REAL, DataSourceTypeEnum.VIRTUAL]))

        # 若指定了 owner_tenant_id，则只搜索该租户下的用户；否则搜索本租户用户与协同租户用户
        if tenant_id := data.get("owner_tenant_id"):
            filter_args.append(Q(data_source__owner_tenant_id=tenant_id))

        queryset = (
            TenantUser.objects.filter(*filter_args)
            .select_related("data_source_user", "data_source")
            .only(
                "id",
                "data_source_user__username",
                "data_source_user__full_name",
                "data_source__type",
                "data_source__owner_tenant_id",
            )
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
        return self.list(request, *args, **kwargs)


class TenantUserLookupApi(OpenWebApiCommonMixin, generics.ListAPIView):
    """
    批量查询用户（包括协同用户与虚拟用户）
    """

    pagination_class = None

    serializer_class = TenantUserLookupOutputSLZ

    def get_queryset(self) -> QuerySet[TenantUser]:
        slz = TenantUserLookupInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 遍历匹配字段列表，构造查询条件
        condition = reduce(
            operator.or_, [self._convert_lookup_to_query(field, data["lookups"]) for field in data["lookup_fields"]]
        )

        filter_args = [Q(tenant_id=self.tenant_id), condition]

        # 若指定了数据源类型，则只查询该类型的用户；否则查询所有数据源类型（除内置管理）的用户
        if data_source_type := data.get("data_source_type"):
            filter_args.append(Q(data_source__type=data_source_type))
        else:
            filter_args.append(Q(data_source__type__in=[DataSourceTypeEnum.REAL, DataSourceTypeEnum.VIRTUAL]))

        # 若指定了 owner_tenant_id，则只查询该租户下的用户；否则查询本租户用户与协同租户用户
        if tenant_id := data.get("owner_tenant_id"):
            filter_args.append(Q(data_source__owner_tenant_id=tenant_id))

        return (
            TenantUser.objects.filter(*filter_args)
            .select_related("data_source_user", "data_source")
            .only(
                "id",
                "data_source_user__username",
                "data_source_user__full_name",
                "data_source__type",
                "data_source__owner_tenant_id",
            )
        )

    @staticmethod
    def _convert_lookup_to_query(field: str, lookups: List[str]) -> Q:
        if field == "full_name":
            return Q(data_source_user__full_name__in=lookups)

        if field == "bk_username":
            return Q(id__in=lookups)

        return Q(data_source_user__username__in=lookups)

    @swagger_auto_schema(
        tags=["open_web.user"],
        operation_id="batch_lookup_user",
        operation_description="批量查询用户",
        query_serializer=TenantUserLookupInputSLZ(),
        responses={status.HTTP_200_OK: TenantUserLookupOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
