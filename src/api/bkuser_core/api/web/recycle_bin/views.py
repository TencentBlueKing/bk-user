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

from django.conf import settings
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser_core.api.web.recycle_bin.serializers import (
    RecycleBinCategoryOutputSlZ,
    RecycleBinDepartmentOutputSlZ,
    RecycleBinProfileOutputSlZ,
    RecycleBinSearchInputSlZ,
)
from bkuser_core.api.web.recycle_bin.utils import (
    check_conflict_before_revert_category,
    list_conflict_before_revert_category,
)
from bkuser_core.api.web.utils import get_category_display_name_map, get_operator
from bkuser_core.api.web.viewset import CustomPagination
from bkuser_core.bkiam.permissions import IAMAction, ManageCategoryPermission, Permission
from bkuser_core.categories.constants import CategoryStatus
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.error_codes import error_codes
from bkuser_core.departments.models import Department
from bkuser_core.profiles.constants import ProfileStatus
from bkuser_core.profiles.models import Profile
from bkuser_core.recycle_bin.constants import RecycleBinObjectType
from bkuser_core.recycle_bin.models import RecycleBin
from bkuser_core.recycle_bin.signals import post_category_hard_delete, post_category_revert
from bkuser_core.recycle_bin.tasks import hard_delete_category_related_resource

logger = logging.getLogger(__name__)


class RecycleBinCategoryListApi(generics.ListAPIView):
    """
    回收站：目录展示
    """

    serializer_class = RecycleBinCategoryOutputSlZ
    queryset = RecycleBin.objects.filter(object_type=RecycleBinObjectType.CATEGORY.value)
    pagination_class = CustomPagination

    def get_queryset(self):
        input_slz = RecycleBinSearchInputSlZ(data=self.request.query_params)
        input_slz.is_valid(raise_exception=True)
        data = input_slz.validated_data

        keyword = data.get("keyword")
        queryset = self.queryset
        # TODO 此处通过大表模糊查询，获取小表对象，待更好的方案进行优化
        if keyword:
            category_ids = ProfileCategory.objects.filter(
                Q(domain__icontains=keyword) | Q(display_name__icontains=keyword),
                enabled=False,
                status=CategoryStatus.DELETED.value,
            ).values_list("id", flat=True)
            queryset = queryset.filter(object_id__in=category_ids)

        # 只返回有权限的
        operator = get_operator(self.request)
        if settings.ENABLE_IAM:
            fs = Permission().make_filter_of_category(operator, IAMAction.VIEW_CATEGORY, category_id_key="object_id")
            queryset = queryset.filter(fs)

        return queryset.all()

    def get_serializer_context(self):
        output_slz_context = super(RecycleBinCategoryListApi, self).get_serializer_context()
        categories = ProfileCategory.objects.all()
        category_map: dict = {}
        for category in categories:
            category_map[category.id] = category

        output_slz_context.update(
            {
                "category_map": category_map,
            }
        )
        return output_slz_context


class RecycleBinDepartmentListApi(generics.ListAPIView):
    """
    回收站：组织展示
    """

    serializer_class = RecycleBinDepartmentOutputSlZ
    queryset = RecycleBin.objects.filter(object_type=RecycleBinObjectType.DEPARTMENT.value)
    pagination_class = CustomPagination

    def get_queryset(self):
        input_slz = RecycleBinSearchInputSlZ(data=self.request.query_params)
        input_slz.is_valid(raise_exception=True)
        data = input_slz.validated_data

        keyword = data.get("keyword")
        queryset = self.queryset
        # TODO 此处通过大表模糊查询，获取小表对象，待更好的方案进行优化
        if keyword:
            department_ids = Department.objects.filter(name__icontains=keyword, enabled=False).values_list(
                "id", flat=True
            )
            queryset = queryset.filter(object_id__in=department_ids)

        # 只返回有目录查看权限的对应部门数据
        operator = get_operator(self.request)
        if settings.ENABLE_IAM:
            fs = Permission().make_filter_of_category(operator, IAMAction.VIEW_CATEGORY)
            department_ids = Department.objects.filter(fs, enabled=False).values_list("id", flat=True)
            queryset = queryset.filter(object_id__in=department_ids)

        return queryset.all()

    def get_serializer_context(self):
        output_slz_context = super(RecycleBinDepartmentListApi, self).get_serializer_context()

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if not page:
            return output_slz_context

        department_ids = [item.object_id for item in page]

        departments = Department.objects.filter(id__in=department_ids)

        department_map: dict = {}
        for department in departments:
            department_map[department.id] = department

        category_display_name_map = get_category_display_name_map()

        output_slz_context.update(
            {
                "category_display_name_map": category_display_name_map,
                "department_map": department_map,
            }
        )
        return output_slz_context


class RecycleBinProfileListApi(generics.ListAPIView):
    """
    回收站：人员展示
    """

    serializer_class = RecycleBinProfileOutputSlZ
    queryset = RecycleBin.objects.filter(object_type=RecycleBinObjectType.PROFILE.value)
    pagination_class = CustomPagination

    def get_queryset(self):
        input_slz = RecycleBinSearchInputSlZ(data=self.request.query_params)
        input_slz.is_valid(raise_exception=True)
        data = input_slz.validated_data

        keyword = data.get("keyword")
        queryset = self.queryset
        # TODO 此处通过大表模糊查询，获取小表对象，待更好的方案进行优化
        if keyword:
            profile_ids = Profile.objects.filter(
                Q(username__icontains=keyword) | Q(display_name__icontains=keyword),
                enabled=False,
                status=ProfileStatus.DELETED.value,
            ).values_list("id", flat=True)
            queryset = queryset.filter(object_id__in=profile_ids)

        # 只返回有目录查看权限的对应用户数据
        operator = get_operator(self.request)
        if settings.ENABLE_IAM:
            fs = Permission().make_filter_of_category(operator, IAMAction.VIEW_CATEGORY)
            profile_ids = Profile.objects.filter(
                fs,
                enabled=False,
                status=ProfileStatus.DELETED.value,
            ).values_list("id", flat=True)
            queryset = queryset.filter(object_id__in=profile_ids)

        return queryset.all()

    def get_serializer_context(self):
        output_slz_context = super(RecycleBinProfileListApi, self).get_serializer_context()

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if not page:
            return output_slz_context

        profile_ids = [item.object_id for item in page]

        profiles = Profile.objects.filter(id__in=profile_ids)
        profile_map: dict = {}
        for profile in profiles:
            profile_map[profile.id] = profile
        category_display_name_map = get_category_display_name_map()

        output_slz_context.update(
            {
                "category_display_name_map": category_display_name_map,
                "profile_map": profile_map,
            }
        )
        return output_slz_context


class RecycleBinCategoryRevertHardDeleteApi(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [ManageCategoryPermission]

    queryset = ProfileCategory.objects.filter(enabled=False, status=CategoryStatus.DELETED.value)
    lookup_url_kwarg = "id"

    def _check_if_category_in_recycle_bin(self, category_id: str):
        """
        是否在回收站里
        防御性检查，上面queryset已经过滤的是软删除的目录了，理论上会在回收站里
        """
        if not RecycleBin.objects.filter(
            object_type=RecycleBinObjectType.CATEGORY.value, object_id=category_id
        ).exists():
            raise error_codes.CANNOT_FIND_CATEGORY_IN_RECYCLE_BIN.f(category_id=category_id)

    def put(self, request, *args, **kwargs):
        """还原目录"""
        category = self.get_object()
        self._check_if_category_in_recycle_bin(category.id)

        # 检查是否冲突
        check_conflict_before_revert_category(category)

        # 还原
        category.revert()
        # 恢复原本的定时任务，增加审计日志
        post_category_revert.send_robust(
            sender=self, instance=category, operator=request.operator, extra_values={"request": request}
        )

        # 删除回收站记录
        RecycleBin.objects.filter(object_type=RecycleBinObjectType.CATEGORY.value, object_id=category.id).delete()

        return Response(status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """硬删除目录"""
        category = self.get_object()
        self._check_if_category_in_recycle_bin(category.id)

        # 增加审计日志, 删除同步功能
        post_category_hard_delete.send_robust(
            sender=self, instance=category, operator=request.operator, extra_values={"request": request}
        )
        # 异步：删除人员，部门，关系，目录设置
        hard_delete_category_related_resource.delay(category_id=category.id)

        return Response(status=status.HTTP_200_OK)


class RecycleBinCategoryRevertConflictApi(generics.ListAPIView):
    permission_classes = [ManageCategoryPermission]

    queryset = ProfileCategory.objects.filter(enabled=False, status=CategoryStatus.DELETED.value)
    lookup_url_kwarg = "id"

    def get(self, request, *args, **kwargs):
        """检查还原目录是否会冲突"""
        category = self.get_object()
        # 查询冲突
        conflicts = list_conflict_before_revert_category(category)
        return Response(data=conflicts)
