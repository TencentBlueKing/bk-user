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
import functools
import logging
from operator import and_, or_
from typing import List

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .auth import IAMBasicAuthentication
from .constants import ResourceType
from .serializers import (
    IAMFetchInstanceInfoSLZ,
    IAMInstanceRespSLZ,
    IAMListAttrValueSLZ,
    IAMListInstancesSLZ,
    IAMMethodSerializer,
    IAMPageResponseSerializer,
)
from bkuser_core.common.error_codes import error_codes

logger = logging.getLogger(__name__)


class IAMPagination(LimitOffsetPagination):
    def get_limit(self, request):
        serializer = IAMPageResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return serializer.validated_data["page"]["limit"]

    def get_offset(self, request):
        serializer = IAMPageResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return serializer.validated_data["page"]["offset"]


class BaseIAMViewSet(viewsets.ModelViewSet):
    serializer_class = IAMMethodSerializer
    permission_classes: List = [IsAuthenticated]
    pagination_class = IAMPagination
    lookup_field = "id"
    ordering = "order"
    authentication_classes: list = [IAMBasicAuthentication]

    # for iam
    parent_field_map: dict = {}
    resource_type: ResourceType
    available_attr: List = []
    instance_serializer_class = IAMInstanceRespSLZ

    def get_parent_queries(self, parent_params: dict) -> dict:
        return {}

    def distribution(self, request):
        """操作分发"""
        serializer = IAMMethodSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        return getattr(self, validated_data["method"])(request)

    def list_attr(self, request):
        """查询某个资源类型可用于配置权限的属性列表"""
        result = []
        for attr in self.available_attr:
            try:
                field = self.queryset.model._meta.get_field(attr)
            except Exception:  # pylint: disable=broad-except
                logger.warning("attr<%s> is not a field of model<%s>", attr, self.queryset.model)
                continue

            result.append({"id": attr, "display_name": field.verbose_name})

        return Response(data=result)

    def list_attr_value(self, request):
        """获取一个资源类型某个属性的值列表"""
        serializer = IAMListAttrValueSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        _filter = serializer.validated_data.get("filter")
        attr = _filter["attr"]
        if attr not in self.available_attr:
            raise error_codes.FIELDS_NOT_SUPPORTED_YET

        queries = []
        if _filter.get("ids"):
            queries.append(Q(**{f"{attr}__in": _filter["ids"]}))

        if _filter.get("keyword"):
            queries.append(Q(**{f"{attr}__icontains": _filter["keyword"]}))

        if len(queries) == 0:
            results = self.queryset
        elif len(queries) == 1:
            results = self.queryset.filter(queries[0])
        else:
            results = self.queryset.filter(functools.reduce(or_, queries))

        # 去重
        results = list(set(results.values_list(attr, flat=True)))
        page = self.paginate_queryset(results)
        rendered = [{"id": x, "display_name": x} for x in page]
        return Response(data={"count": len(results), "results": rendered})

    def list_instance(self, request):
        """根据过滤条件查询实例"""
        serializer = IAMListInstancesSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        _filter = serializer.validated_data.get("filter")
        queries = []

        if self.parent_field_map and _filter and _filter.get("parent"):
            queries.append(Q(**self.get_parent_queries(_filter.get("parent"))))

        if len(queries) == 0:
            results = self.queryset
        elif len(queries) == 1:
            results = self.queryset.filter(queries[0])
        else:
            results = self.queryset.filter(functools.reduce(or_, queries))

        page = self.paginate_queryset(results)
        return Response(
            data={
                "count": len(results),
                "results": self.instance_serializer_class(
                    page,
                    many=True,
                    id_display_name_pair=ResourceType.get_id_name_pair(self.resource_type),
                ).data,
            }
        )

    def fetch_instance_info(self, request):
        """批量获取资源实例详情"""
        serializer = IAMFetchInstanceInfoSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        _filter = serializer.validated_data.get("filter")
        id_name_pair = ResourceType.get_id_name_pair(self.resource_type)
        results = self.queryset.filter(**{f"{id_name_pair[0]}__in": _filter["ids"]})
        return Response(
            data=self.instance_serializer_class(results, many=True, id_display_name_pair=id_name_pair).data
        )

    def list_instance_by_policy(self, request):
        """根据策略表达式查询资源实例"""
        # TODO: 依赖 sdk，暂不实现

    def search_instance(self, request):
        """搜索资源实例"""
        serializer = IAMListInstancesSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        _filter = serializer.validated_data.get("filter")
        keyword_queries = []
        parent_queries = []

        if _filter and _filter.get("keyword"):
            for _field in ResourceType.get_id_name_pair(self.resource_type):
                keyword_queries.append(Q(**{f"{_field}__icontains": _filter["keyword"]}))

        if self.parent_field_map and _filter and _filter.get("parent"):
            parent_queries.append(Q(**self.get_parent_queries(_filter.get("parent"))))

        def merge_queries(list_q: list) -> list:
            """合并两种查询条件"""
            m_q = []
            for q in list_q:
                if not q:
                    continue
                q = functools.reduce(or_, q)
                m_q.append(q)

            return functools.reduce(and_, m_q)

        merge_queries = merge_queries([keyword_queries, parent_queries])
        if not merge_queries:
            results = self.queryset
        else:
            results = self.queryset.filter(merge_queries)

        page = self.paginate_queryset(results)
        return Response(
            data={
                "count": len(results),
                "results": self.instance_serializer_class(
                    page,
                    many=True,
                    id_display_name_pair=ResourceType.get_id_name_pair(self.resource_type),
                ).data,
            }
        )
