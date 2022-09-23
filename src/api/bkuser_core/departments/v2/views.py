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
from typing import Type

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from bkuser_core.apis.v2.serializers import AdvancedRetrieveSerializer
from bkuser_core.apis.v2.viewset import (
    AdvancedListAPIView,
    AdvancedListSerializer,
    AdvancedModelViewSet,
    AdvancedSearchFilter,
)
from bkuser_core.audit.constants import OperationType
from bkuser_core.audit.utils import audit_general_log
from bkuser_core.categories.cache import get_default_category_domain_from_local_cache
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.cache import clear_cache_if_succeed
from bkuser_core.common.error_codes import error_codes
from bkuser_core.departments.models import Department, DepartmentThroughModel
from bkuser_core.departments.signals import post_department_create
from bkuser_core.departments.v2 import serializers as local_serializers
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.v2.serializers import ProfileMinimalSerializer, RapidProfileSerializer

logger = logging.getLogger(__name__)


class DepartmentViewSet(AdvancedModelViewSet, AdvancedListAPIView):
    queryset = Department.objects.filter()
    serializer_class = local_serializers.DepartmentSerializer
    lookup_field: str = "id"
    filter_backends = [
        AdvancedSearchFilter,
        filters.OrderingFilter,
    ]

    def _param_in_request(self, param_name: str, serializer_class: Type[Serializer], in_query: bool = True) -> bool:
        if in_query:
            slz = serializer_class(data=self.request.query_params)
        else:
            slz = serializer_class(data=self.request.data)

        slz.is_valid(raise_exception=True)
        return slz.validated_data.get(param_name)

    def get_serializer_class(self):
        """Serializer 路由"""
        if self.action in ("list",):
            if self._param_in_request(
                "with_ancestors",
                local_serializers.DepartmentListSerializer,
                in_query=True,
            ):
                return local_serializers.DepartmentsWithAncestorsSerializer
        elif self.action in ("retrieve",):
            if self._param_in_request(
                "with_ancestors",
                local_serializers.DepartmentRetrieveSerializer,
                in_query=True,
            ):
                return local_serializers.DepartmentsWithAncestorsSerializer
            else:
                return local_serializers.DepartmentWithChildrenSLZ

        return self.serializer_class

    @method_decorator(cache_page(settings.GLOBAL_CACHES_TIMEOUT))
    @swagger_auto_schema(query_serializer=AdvancedListSerializer())
    def list(self, request, *args, **kwargs):
        # NOTE: 用于两套用户管理之间的数据同步
        if settings.SYNC_API_PARAM in request.query_params:
            request.META[settings.FORCE_RAW_RESPONSE_HEADER] = "true"

        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(settings.GLOBAL_CACHES_TIMEOUT))
    @swagger_auto_schema(
        query_serializer=local_serializers.DepartmentRetrieveSerializer(),
        responses={"200": local_serializers.DepartmentsWithAncestorsSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @method_decorator(cache_page(settings.GLOBAL_CACHES_TIMEOUT))
    @swagger_auto_schema(query_serializer=AdvancedRetrieveSerializer())
    def get_ancestor(self, request, *args, **kwargs):
        """获取父级部门"""
        instance = self.get_object()

        try:
            department_objs = instance.get_ancestors(include_self=True).filter(enabled=True)
        except Department.DoesNotExist:
            department_objs = []

        return Response(data=local_serializers.DepartmentSimpleSerializer(department_objs, many=True).data)

    @method_decorator(cache_page(settings.GLOBAL_CACHES_TIMEOUT))
    @swagger_auto_schema(query_serializer=AdvancedRetrieveSerializer())
    def get_children(self, request, *args, **kwargs):
        """获取子部门列表"""
        instance = self.get_object()

        try:
            department_objs = instance.get_children().filter(enabled=True)
        except Department.DoesNotExist:
            department_objs = []

        return Response(data=local_serializers.DepartmentSimpleSerializer(department_objs, many=True).data)

    @method_decorator(cache_page(settings.GLOBAL_CACHES_TIMEOUT))
    @swagger_auto_schema(query_serializer=local_serializers.DepartmentGetProfilesSerializer())
    def get_profiles(self, request, *args, **kwargs):
        """获取部门内的人员"""
        serializer = local_serializers.DepartmentGetProfilesSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()

        # 这个参数esb文档中有, 有用户调用
        recursive = serializer.validated_data["recursive"]
        # FIXME: 这个在 esb 文档中没有提到, 需要确认是否可以下线
        wildcard_search = serializer.validated_data.get("wildcard_search")

        # 这个参数esb文档中有, 有用户调用
        profiles = instance.get_profiles(recursive=recursive, wildcard_search=wildcard_search)
        # 当用户请求数据时，判断其是否强制输出原始 username
        # if not force_use_raw_username(request): # always be true

        # 直接在 DB 中拼接 username & domain，比在 serializer 中快很多
        # default_domain = ProfileCategory.objects.get_default().domain
        default_domain = get_default_category_domain_from_local_cache()
        profiles = profiles.extra(
            select={"username": "if(`domain`= %s, username, CONCAT(username, '@', domain))"},
            select_params=(default_domain,),
        )

        page = self.paginate_queryset(profiles)
        # NOTE: RapidProfileSerializer 中的 last_login_time/extras会导致放大查询 => * 2
        _serializer = RapidProfileSerializer
        if page is not None:
            context = self.get_serializer_context()
            return self.get_paginated_response(_serializer(page, many=True, context=context).data)

        # NOTE: no_page=True, will hit this branch. should not use no_page=True in the future
        serializer_fields = list(_serializer().get_fields().keys())
        model_fields_keys = [x.name for x in profiles.model._meta.get_fields()]
        values_fields = [x for x in serializer_fields if x in model_fields_keys]

        # 全量数据太大，使用 serializer 效率非常低
        # 由于存在多对多字段，所以返回列表会平铺展示，同一个 username 会多次展示
        # https://docs.djangoproject.com/en/3.2/ref/models/querysets/#values
        return Response(data=list(profiles.only(*values_fields).values(*values_fields)))

    @audit_general_log(operate_type=OperationType.UPDATE.value)
    @method_decorator(clear_cache_if_succeed)
    @swagger_auto_schema(
        request_body=local_serializers.DepartmentAddProfilesSerializer,
        responses={"201": ProfileMinimalSerializer(many=True)},
    )
    def add_profiles(self, request, *args, **kwargs):
        """在部门内添加人员"""
        instance = self.get_object()

        serializer = local_serializers.DepartmentAddProfilesSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        profiles = Profile.objects.filter(id__in=serializer.validated_data["profile_id_list"])
        for profile in profiles:
            instance.add_profile(profile)

        return Response(data=ProfileMinimalSerializer(profiles, many=True).data)

    @method_decorator(clear_cache_if_succeed)
    def create(self, request, *args, **kwargs):
        """创建部门"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        if not validated_data.get("category_id", None):
            serializer.validated_data["category_id"] = ProfileCategory.objects.get_default().id
        else:
            if not ProfileCategory.objects.check_writable(validated_data["category_id"]):
                raise error_codes.CANNOT_MANUAL_WRITE_INTO

        category = ProfileCategory.objects.get(id=validated_data["category_id"])
        if not serializer.validated_data.get("parent"):
            self.check_object_permissions(request, obj=category)

            # 不传 parent 默认为根部门
            serializer.validated_data["level"] = 0
            max_order = list(
                Department.objects.filter(
                    enabled=True, category_id=validated_data["category_id"], level=0
                ).values_list("order", flat=True)
            )
            max_order = max(max_order or [0])
        else:
            self.check_object_permissions(request, obj=serializer.validated_data.get("parent"))
            max_order = serializer.validated_data["parent"].get_max_order_in_children()

        serializer.validated_data["order"] = max_order + 1
        # 同一个组织下，不能有同名子部门
        try:
            instance = Department.objects.get(
                parent_id=serializer.validated_data.get("parent"),
                name=validated_data["name"],
                category_id=validated_data["category_id"],
            )
            # 若是已删除的，将直接启用，未删除的抛出重复错误
            if not instance.enabled:
                instance.enable()
            else:
                raise error_codes.DEPARTMENT_NAME_CONFLICT
        except Department.DoesNotExist:
            instance = serializer.save()

        post_department_create.send(
            sender=self, instance=instance, operator=request.operator, extra_values={"request": request}
        )
        return Response(self.serializer_class(instance).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=local_serializers.DepartmentUpdateSerializer(),
        responses={200: local_serializers.DepartmentSerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        # check permission first, call check_object_permission
        instance = self.get_object()
        self.check_object_permissions(request, obj=instance)

        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=local_serializers.DepartmentUpdateSerializer(),
        responses={200: local_serializers.DepartmentSerializer()},
    )
    def update(self, request, *args, **kwargs):
        """更新部门"""
        serializer = local_serializers.DepartmentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        instance = self.get_object()

        # 只允许本地目录修改
        if not ProfileCategory.objects.check_writable(instance.category_id):
            raise error_codes.CANNOT_MANUAL_WRITE_INTO
        if validated_data.get("name", None):
            if Department.objects.filter(parent=instance.parent, name=validated_data["name"]).exists():
                raise error_codes.DEPARTMENT_NAME_CONFLICT

        return super().update(request, *args, **kwargs)


class DepartmentProfileEdgeViewSet(AdvancedModelViewSet, AdvancedListAPIView):
    """部门边"""

    queryset = DepartmentThroughModel.objects.filter(profile__enabled=True, department__enabled=True)
    serializer_class = local_serializers.DepartmentProfileEdgesSLZ
    ordering = ["id"]
