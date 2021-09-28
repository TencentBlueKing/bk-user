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
from collections import OrderedDict
from operator import or_
from typing import Any, Dict, List, Optional

from bkuser_core.audit.constants import OperationEnum
from bkuser_core.audit.utils import create_general_log
from bkuser_core.bkiam.exceptions import IAMPermissionDenied
from bkuser_core.bkiam.filters import IAMFilter
from bkuser_core.bkiam.permissions import IAMPermission, IAMPermissionExtraInfo
from bkuser_core.common.cache import clear_cache_if_succeed
from bkuser_core.common.error_codes import error_codes
from bkuser_core.common.serializers import (
    AdvancedListSerializer,
    AdvancedRetrieveSerialzier,
    EmptySerializer,
    is_custom_fields_enabled,
)
from django.conf import settings
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.db.models import ManyToOneRel, Q, QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, serializers, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from bkuser_global.utils import force_str_2_bool

from .constants import LOOKUP_FIELD_NAME, LOOKUP_PARAM

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = settings.MAX_PAGE_SIZE

    def paginate_queryset(self, queryset, request, view=None):
        # FIXME: REMOVE no_page in future version
        if force_str_2_bool(request.query_params.get("no_page", False)):
            return None

        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("results", data),
                ]
            )
        )


class DynamicFieldsMixin:
    def _get_model_field_names(self):
        """获取 model 所有字段"""
        fields = self.queryset.model._meta.get_fields()

        # 过滤掉多对多
        return [getattr(f, "name") for f in fields if not isinstance(f, ManyToOneRel)]

    def _check_fields(self, fields):
        """检查用户传入的 fields 是否在 DB 字段中"""
        if not fields:
            return

        not_model_fields = set(fields) - set(self._get_model_field_names())
        if not not_model_fields == set():
            raise error_codes.FIELDS_NOT_SUPPORTED_YET.f(",".join(not_model_fields))

    def _get_list_query_param(self, field_name, divide_char=",", request=None) -> Optional[List]:
        """从 query_param 中获取列表参数
        TODO: 改造成 serializer
        """
        target_request = getattr(self, "request", None) or request
        if not target_request:
            raise ValueError("no request available.")

        params = target_request.query_params.get(field_name)

        if params:
            params = params.split(divide_char)
            # remove spaces & 去重
            params = list({x.replace("&nbsp;", "") for x in params if x})

        return params or None

    def _get_fields(self, request=None) -> Optional[List]:
        """获取用户传入的 fields
        TODO: 改造成 serializer
        """
        return self._get_list_query_param("fields", request=request)

    def _ensure_enabled_field(self, request, fields: Optional[List] = None):
        """确保用户在传入 include_disabled_field 时，返回内容包含 enabled 字段"""
        if not fields:
            return
        if (
            "enabled" in fields
            or getattr(self, "include_disabled_field", "include_disabled") not in request.query_params
        ):
            return
        fields.append("enabled")


class AdvancedSearchFilter(filters.SearchFilter, DynamicFieldsMixin):
    SEARCH_PARAM = "lookup_field"
    SOFT_DELETE_MODELNAMES = ("Profile", "Department", "ProfileCategory")
    WILDCARD_SEARCH_PARAM = "wildcard_search"
    WILDCARD_SEARCH_FIELDS_PARAM = "wildcard_search_fields"
    BEST_MATCH_PARAM = "best_match"

    serializer_class = AdvancedListSerializer

    @staticmethod
    def _try_best_match(
        best_match: bool,
        queryset: QuerySet,
        condition_str: str,
        params: Optional[list] = None,
    ):
        # 最短匹配排在前面
        if best_match:
            extra_params = {"select": {"lookup_field_length": f"Length({condition_str})"}}  # type: Dict[str, Any]
            if params:
                extra_params["select_params"] = params

            return queryset.extra(**extra_params).order_by("lookup_field_length")

        return queryset

    @staticmethod
    def make_time_filter(query_data: dict) -> Q:
        """拼接时间过滤"""
        _f = {}
        since, until = query_data.get("since"), query_data.get("until")
        time_field = query_data.get("time_field")
        if since:
            _f[f"{time_field}__gte"] = since
        if until:
            _f[f"{time_field}__lte"] = until

        return Q(**_f)

    def make_lookups(self, query_data: dict, queryset: QuerySet, search_field: str) -> QuerySet:
        """拼装搜索查询语句，当不存在搜索时返回空列表"""
        exact_lookups, fuzzy_lookups = query_data.get("exact_lookups"), query_data.get("fuzzy_lookups")
        target_lookups = []
        if exact_lookups:
            target_lookups = [Q(**{search_field: x}) for x in exact_lookups]
        elif fuzzy_lookups:
            target_lookups = [Q(**{"{}__icontains".format(search_field): x}) for x in fuzzy_lookups]

        target_lookups.append(self.make_time_filter(query_data))
        if not target_lookups:
            return queryset

        # 最短匹配排在前面
        if fuzzy_lookups:
            self._try_best_match(bool(query_data.get("best_match")), queryset, search_field)

        # 当只有一个搜索内容时，直接返回结果
        if len(target_lookups) == 1:
            return queryset.filter(target_lookups[0])

        # 把多个条件并起来
        query = functools.reduce(or_, target_lookups)
        return queryset.filter(query)

    def filter_queryset(self, request, queryset, view):
        # 首先筛选字段
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(True)
        query_data = serializer.validated_data

        if queryset.model.__name__ in self.SOFT_DELETE_MODELNAMES and not force_str_2_bool(
            request.query_params.get(view.include_disabled_field, False)
        ):
            queryset = queryset.filter(enabled=True)

        fields = query_data.get("fields", [])
        if fields:
            # 需要将多对多的关系字段先减去，避免 prefetch 失败
            fields = list(set(fields) - set(view.relation_fields))
            # 这里使用 only 而不是 values，是为了保证 queryset 保持为 QuerySet
            queryset = queryset.only(*fields)

        # 0. 优先调用方传入搜索字段，否则从 views 配置中获取
        search_field = query_data.get(self.search_param) or getattr(view, self.search_param, None)

        if not search_field:
            raise serializers.ValidationError("Search field should be specific by call.")

        # 1. 首先判断是否启用了 wildcard search，是则最高优先处理
        wildcard_search = query_data.get(self.WILDCARD_SEARCH_PARAM)
        wildcard_search_fields = query_data.get(self.WILDCARD_SEARCH_FIELDS_PARAM)

        if wildcard_search and wildcard_search_fields:
            target_lookups = [Q(**{"{}__icontains".format(x): wildcard_search}) for x in wildcard_search_fields]
            queryset = queryset.filter(functools.reduce(or_, target_lookups))

        # 2. 单字段搜索
        return self.make_lookups(query_data, queryset, search_field)


class AdvancedModelViewSet(viewsets.ModelViewSet, DynamicFieldsMixin):
    """ModelViewSet 功能增强集合类
    - fields 用户定义返回字段
    """

    permission_classes = [IAMPermission]
    # 使用 filter 进行过滤的操作
    iam_filter_actions: tuple = ()

    def filter_queryset(self, queryset) -> QuerySet:
        filter_backends = list(self.filter_backends)
        # 只针对 list 接口增加 filter，其他操作都通过 check_object 判断
        if self.action in self.iam_filter_actions:
            filter_backends.append(IAMFilter)

        for backend in filter_backends:
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def check_object_permissions(self, request, obj):
        """增加 obj 到 extra_info"""
        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                self.permission_denied(request, message=getattr(permission, "message", None), obj=obj)

    def permission_denied(self, request, message=None, obj=None):
        """针对 IAM 注入相关信息"""
        raise IAMPermissionDenied(
            detail=message,
            extra_info=IAMPermissionExtraInfo.from_request(request, obj=obj).to_dict(),
        )

    def get_object(self):
        # 暂存
        _default_lookup_field = self.lookup_field

        self.lookup_url_kwarg = LOOKUP_FIELD_NAME

        try:
            request_lookup_field = self.request.query_params[LOOKUP_PARAM]
            self.lookup_field = request_lookup_field
        except KeyError:
            """使用默认查询字段"""

        try:
            return super().get_object()
        except FieldError:
            # TODO: 用户传递了错误的 field 应该 raise 出 400 的报错
            self.lookup_field = _default_lookup_field
            return super().get_object()

    @method_decorator(cache_page(settings.GLOBAL_CACHES_TIMEOUT))
    @swagger_auto_schema(query_serializer=AdvancedRetrieveSerialzier())
    def retrieve(self, request, *args, **kwargs):
        """获取详细信息"""
        fields = self._get_fields()
        self._check_fields(fields)

        instance = self.get_object()
        return Response(
            data=self.get_serializer(instance, fields=fields).data,
            status=status.HTTP_200_OK,
        )

    @method_decorator(clear_cache_if_succeed)
    @swagger_auto_schema(query_serializer=AdvancedRetrieveSerialzier())
    def update(self, request, *args, **kwargs):
        """更新对象"""
        instance = self.get_object()
        result = super().update(request, *args, **kwargs)

        create_general_log(
            operator=request.operator,
            operate_type=OperationEnum.UPDATE.value,
            operator_obj=instance,
            request=request,
        )
        return result

    @method_decorator(clear_cache_if_succeed)
    @swagger_auto_schema(query_serializer=AdvancedRetrieveSerialzier())
    def destroy(self, request, *args, **kwargs):
        """删除对象"""
        instance = self.get_object()
        create_general_log(
            operator=request.operator,
            operate_type=OperationEnum.DELETE.value,
            operator_obj=instance,
            request=request,
        )

        return super().destroy(request, *args, **kwargs)

    @method_decorator(clear_cache_if_succeed)
    @swagger_auto_schema(query_serializer=AdvancedRetrieveSerialzier(), request_body=EmptySerializer)
    def restoration(self, request, lookup_value):
        """软删除对象恢复"""
        instance = self.get_object()
        if instance.enabled:
            raise error_codes.RESOURCE_ALREADY_ENABLED
        try:
            instance.enable()
        except Exception as why:
            # TODO: 基于 issue71 更新操作日志
            logger.exception("failed to restoration instance: %s, error: %s", instance, why)
        else:
            create_general_log(
                operator=request.operator,
                operate_type=OperationEnum.RESTORATION.value,
                operator_obj=instance,
                request=request,
                extra_info={"action": f"restoration {instance._meta.model_name}.{self.lookup_field}-{lookup_value}"},
            )
        return Response()


class AdvancedListAPIView(ListAPIView, DynamicFieldsMixin):
    """列表查询功能增强类"""

    filter_backends = [AdvancedSearchFilter, filters.OrderingFilter]
    pagination_class = StandardResultsSetPagination
    exclude_fields: List = []
    permission_classes = [IAMPermission]
    include_disabled_field = "include_disabled"
    relation_fields: list = []

    @method_decorator(cache_page(settings.GLOBAL_CACHES_TIMEOUT))
    @swagger_auto_schema(query_serializer=AdvancedListSerializer())
    def list(self, request, *args, **kwargs):
        """获取对象列表"""
        self.check_permissions(request)
        _query_slz = AdvancedListSerializer(data=request.query_params)
        _query_slz.is_valid(True)
        query_data = _query_slz.validated_data

        fields = query_data.get("fields", None)
        self._ensure_enabled_field(request, fields=fields)
        self._check_fields(fields)

        try:
            queryset = self.filter_queryset(self.get_queryset())
        except IAMPermissionDenied:
            # pass to exception handler
            raise
        except Exception:
            logger.exception("query failed")
            raise error_codes.QUERY_PARAMS_ERROR

        kwargs = {"many": True}
        if is_custom_fields_enabled(self.get_serializer()):
            # 未继承 CustomFieldsModelSerializer 的 serializer 不接收 fields 字段
            kwargs["fields"] = fields

        page = self.paginate_queryset(queryset)
        serializer_class = self.get_serializer_class()
        if page is not None:
            serializer = serializer_class(page, **kwargs)
            return self.get_paginated_response(serializer.data)

        # 使用了 serializer 可能会有性能问题
        serializer = serializer_class(queryset, **kwargs)
        return Response(serializer.data)


class AdvancedBatchOperateViewSet(viewsets.ModelViewSet, DynamicFieldsMixin):
    """批量操作接口"""

    CATEGORY_SENSITIVE = True

    @method_decorator(cache_page(settings.GLOBAL_CACHES_TIMEOUT))
    def multiple_retrieve(self, request):
        """批量获取"""
        ids = self._get_list_query_param(field_name="query_ids") or []
        instances = self.queryset.filter(pk__in=ids)
        return Response(self.serializer_class(instances, many=True).data)

    @method_decorator(clear_cache_if_succeed)
    def multiple_update(self, request):
        """批量更新，必须传递 id 作为查找字段"""
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        query_objs = serializer.validated_data
        updating_instances = []
        for obj in query_objs:
            try:
                instance = self.queryset.get(pk=obj["id"])
            except ObjectDoesNotExist:
                logger.warning(
                    "obj <%s-%s> not found or already been deleted.",
                    self.queryset.model,
                    obj,
                )
                continue
            else:
                create_general_log(
                    operator=request.operator,
                    operate_type=OperationEnum.UPDATE.value,
                    operator_obj=instance,
                    request=request,
                )

            if self.CATEGORY_SENSITIVE:
                # TODO: 限制非本地目录进行修改
                pass

            single_serializer = serializer_class(instance=instance, data=obj)
            single_serializer.is_valid(raise_exception=True)
            single_serializer.save()
            updating_instances.append(instance)

        return Response(self.serializer_class(updating_instances, many=True).data)

    @method_decorator(clear_cache_if_succeed)
    def multiple_delete(self, request):
        """批量删除"""
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        query_objs = serializer.validated_data
        for obj in query_objs:
            try:
                instance = self.queryset.get(pk=obj["id"])
                create_general_log(
                    operator=request.operator,
                    operate_type=OperationEnum.DELETE.value,
                    operator_obj=instance,
                    request=request,
                )

                instance.delete()
            except ObjectDoesNotExist:
                logger.warning(
                    "obj <%s-%s> not found or already been deleted.",
                    self.queryset.model,
                    obj,
                )
                continue

        return Response()
