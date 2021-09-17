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
from typing import Type

from bkuser_core.audit.constants import OperationEnum
from bkuser_core.audit.utils import create_general_log
from bkuser_core.bkiam.exceptions import IAMPermissionDenied
from bkuser_core.bkiam.permissions import IAMPermissionExtraInfo
from bkuser_core.bkiam.utils import need_iam
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.cache import clear_cache_if_succeed
from bkuser_core.common.error_codes import error_codes
from bkuser_core.common.serializers import AdvancedRetrieveSerialzier, EmptySerializer
from bkuser_core.common.viewset import (
    AdvancedBatchOperateViewSet,
    AdvancedListAPIView,
    AdvancedModelViewSet,
    AdvancedSearchFilter,
)
from bkuser_core.profiles.models import DynamicFieldInfo, Profile
from bkuser_core.profiles.serializers import ProfileMinimalSerializer, ProfileSerializer, RapidProfileSerializer
from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from ..profiles.utils import force_use_raw_username
from . import serializers as local_serializers
from .models import Department, DepartmentThroughModel


class DepartmentViewSet(AdvancedModelViewSet, AdvancedListAPIView):
    queryset = Department.objects.filter()
    serializer_class = local_serializers.DepartmentSerializer
    lookup_field: str = "id"
    filter_backends = [
        AdvancedSearchFilter,
        filters.OrderingFilter,
    ]
    iam_filter_actions = ("list", "list_tops")

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

    def get_serializer_context(self):
        origin = super().get_serializer_context()
        origin.update({"extra_defaults": DynamicFieldInfo.objects.get_extras_default_values()})
        return origin

    @method_decorator(cache_page(settings.GLOBAL_CACHES_TIMEOUT))
    @swagger_auto_schema(
        query_serializer=local_serializers.DepartmentRetrieveSerializer(),
        responses={"200": local_serializers.DepartmentsWithAncestorsSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @method_decorator(cache_page(settings.GLOBAL_CACHES_TIMEOUT))
    @swagger_auto_schema(query_serializer=AdvancedRetrieveSerialzier())
    def get_ancestor(self, request, *args, **kwargs):
        """获取父级部门"""
        instance = self.get_object()

        try:
            department_objs = instance.get_ancestors(include_self=True).filter(enabled=True)
        except Department.DoesNotExist:
            department_objs = []

        return Response(data=local_serializers.DepartmentSimpleSerializer(department_objs, many=True).data)

    @method_decorator(cache_page(settings.GLOBAL_CACHES_TIMEOUT))
    @swagger_auto_schema(query_serializer=AdvancedRetrieveSerialzier())
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

        recursive = serializer.validated_data["recursive"]
        wildcard_search = serializer.validated_data.get("wildcard_search")

        profiles = instance.get_profiles(recursive=recursive, wildcard_search=wildcard_search)
        # 当用户请求数据时，判断其是否强制输出原始 username
        if not force_use_raw_username(request):
            # 直接在 DB 中拼接 username & domain，比在 serializer 中快很多
            default_domain = ProfileCategory.objects.get_default().domain
            profiles = profiles.extra(
                select={"username": "if(`domain`= %s, username, CONCAT(username, '@', domain))"},
                select_params=(default_domain,),
            )

        page = self.paginate_queryset(profiles)
        _serializer = RapidProfileSerializer
        if page is not None:
            return self.get_paginated_response(_serializer(page, many=True).data)

        serializer_fields = list(_serializer().get_fields().keys())
        # 全量数据太大，使用 serializer 效率非常低
        # 由于存在多对多字段，所以返回列表会平铺展示，同一个 username 会多次展示
        # https://docs.djangoproject.com/en/3.2/ref/models/querysets/#values
        return Response(data=list(profiles.only(*serializer_fields).values(*serializer_fields)))

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

        # 审计记录
        create_general_log(
            operator=request.operator,
            operate_type=OperationEnum.UPDATE.value,
            operator_obj=instance,
            request=request,
        )
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

        # 审计记录
        create_general_log(
            operator=request.operator,
            operate_type=OperationEnum.CREATE.value,
            operator_obj=instance,
            request=request,
        )
        return Response(self.serializer_class(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """更新部门"""
        serializer = self.serializer_class(data=request.data)
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

    @method_decorator(cache_page(settings.GLOBAL_CACHES_TIMEOUT))
    @swagger_auto_schema(query_serializer=EmptySerializer())
    def list_tops(self, request, *args, **kwargs):
        """获取最顶层的组织列表[权限中心亲和]"""

        if not need_iam(request):
            queryset = self.get_queryset().filter(level=0)
        else:
            # 1. 拿到权限中心里授过权的全列表
            queryset = self.filter_queryset(self.get_queryset())

            if not queryset:
                return Response(data=self.get_serializer(queryset, many=True).data)

            # 2. 如果父节点已经授过权，剔除子节点
            # TODO: 相较于手动遍历快了很多，但还是不够快，有优化空间
            descendants = Department.tree_objects.get_queryset_descendants(queryset=queryset, include_self=False)
            queryset = queryset.exclude(id__in=descendants.values_list("id", flat=True))

        if not queryset:
            raise IAMPermissionDenied(
                detail=_("您没有该操作的权限，请在权限中心申请"),
                extra_info=IAMPermissionExtraInfo.from_request(request).to_dict(),
            )

        return Response(data=self.get_serializer(queryset, many=True).data)


class BatchDepartmentsViewSet(AdvancedBatchOperateViewSet):
    serializer_class = local_serializers.DepartmentWithChildrenSLZ
    queryset = Department.objects.filter(enabled=True)

    @swagger_auto_schema(
        query_serializer=local_serializers.BatchDepartmentsRetrieveSerializer(),
        responses={"200": ProfileSerializer(many=True)},
    )
    def multiple_retrieve_profiles(self, request):
        """批量获取组织的用户"""
        serializer = local_serializers.BatchDepartmentsRetrieveSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        ids = self._get_list_query_param(field_name="department_ids")
        recursive = serializer.validated_data["recursive"]

        ids = Department.tree_objects.get_queryset_descendants(
            queryset=Department.objects.filter(id__in=ids), include_self=recursive
        ).values_list("id", flat=True)

        profile_ids = DepartmentThroughModel.objects.filter(department_id__in=ids).values_list("profile_id", flat=True)
        profiles = Profile.objects.filter(id__in=profile_ids)
        return Response(data=ProfileSerializer(profiles, many=True).data)


class DepartmentProfileEdgeViewSet(AdvancedModelViewSet, AdvancedListAPIView):
    """部门边"""

    queryset = DepartmentThroughModel.objects.filter(profile__enabled=True, department__enabled=True)
    serializer_class = local_serializers.DepartmentProfileEdgesSLZ
    ordering = ["id"]
