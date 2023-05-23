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

from django.db import transaction
from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response

from bkuser_core.api.web.recycle_bin.constants import CategoryCheckMessageEnum
from bkuser_core.api.web.recycle_bin.serializers import (
    BatchCategoryHardDeleteInputSlZ,
    BatchCategoryRevertInputSlZ,
    CategoryRevertCheckResultOutputSlZ,
    CategoryRevertResultOutputSlZ,
    RecycleBinCategoryOutputSlZ,
    RecycleBinDepartmentOutputSlZ,
    RecycleBinProfileOutputSlZ,
    RecycleBinSearchInputSlZ,
)
from bkuser_core.api.web.recycle_bin.utils import check_category_in_recycle_bin
from bkuser_core.api.web.utils import get_category_display_name_map
from bkuser_core.api.web.viewset import CustomPagination
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
                status=CategoryStatus.INACTIVE.value,
            ).values_list("id", flat=True)
            queryset = queryset.filter(object_id__in=category_ids)
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


class RecycleBinBatchCategoryRevertCheckApi(generics.CreateAPIView):
    queryset = RecycleBin.objects.filter(object_type=RecycleBinObjectType.CATEGORY.value)
    serializer_class = CategoryRevertCheckResultOutputSlZ

    def post(self, request, *args, **kwargs):
        input_slz = BatchCategoryRevertInputSlZ(data=request.data)
        input_slz.is_valid(raise_exception=True)
        data = input_slz.validated_data

        # 检查目录是否在回收站
        for category_id in data["category_ids"]:
            check_category_in_recycle_bin(category_id=category_id)

        # 待还原，需进行检查的软删除目录
        check_detail_list: list = []
        for category in ProfileCategory.objects.filter(id__in=data["category_ids"]):
            check_detail: dict = {
                "category_id": category.id,
                "check_status": True,
                "error_message": "",
            }
            # 重名检查
            if ProfileCategory.objects.filter(enabled=True, display_name=category.display_name).exists():
                check_detail["check_status"] = False
                check_detail["error_message"] = CategoryCheckMessageEnum.DUPLICATE_DISPLAY_NAME.value
                continue
            # 重登录域检查
            if ProfileCategory.objects.filter(enabled=True, domain=category.domain).exists():
                check_detail["check_status"] = False
                check_detail["error_message"] = CategoryCheckMessageEnum.DUPLICATE_DOMAIN.value
                continue

            check_detail_list.append(check_detail)

        return Response(data=self.serializer_class(instance=check_detail_list, many=True).data)


class RecycleBinBatchCategoryRevertApi(generics.CreateAPIView):
    queryset = RecycleBin.objects.filter(object_type=RecycleBinObjectType.CATEGORY.value)
    serializer_class = CategoryRevertResultOutputSlZ

    def post(self, request, *args, **kwargs):
        input_slz = BatchCategoryRevertInputSlZ(data=request.data)
        input_slz.is_valid(raise_exception=True)
        data = input_slz.validated_data

        # 检查目录是否在回收站
        for category_id in data["category_ids"]:
            check_category_in_recycle_bin(category_id=category_id)

        categories = ProfileCategory.objects.filter(id__in=data["category_ids"])

        # 二次检查
        for category in categories:
            # 重名检查
            if ProfileCategory.objects.filter(enabled=True, display_name=category.display_name).exists():
                raise error_codes.REVERT_CATEGORIES_FAILED.f(
                    category_id=category.id,
                    error_message=CategoryCheckMessageEnum.DUPLICATE_DISPLAY_NAME.value,
                )
            # 重登录域检查
            if ProfileCategory.objects.filter(enabled=True, domain=category.domain).exists():
                raise error_codes.REVERT_CATEGORIES_FAILED.f(
                    category_id=category.id,
                    error_message=CategoryCheckMessageEnum.DUPLICATE_DOMAIN.value,
                )

        # 还原结果初始化
        revert_results: dict = {
            "successful_count": 0,
        }
        reverted_category_ids: list = []
        with transaction.atomic():
            for category in categories:
                category.revert()
                # 恢复原本的定时任务，增加审计日志
                post_category_revert.send_robust(
                    sender=self, instance=category, operator=request.operator, extra_values={"request": request}
                )
                revert_results["successful_count"] += 1
                reverted_category_ids.append(category.id)

        # 删除映射记录
        self.queryset.filter(object_id__in=reverted_category_ids).delete()

        return Response(self.serializer_class(revert_results).data)


class RecycleBinCategoryBatchHardDeleteApi(generics.DestroyAPIView):
    queryset = RecycleBin.objects.filter(object_type=RecycleBinObjectType.CATEGORY.value)

    def destroy(self, request, *args, **kwargs):
        slz = BatchCategoryHardDeleteInputSlZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 检查目录是否在回收站
        for category_id in data["category_ids"]:
            check_category_in_recycle_bin(category_id=category_id)

        # 删除关联资源
        categories_ids = data["category_ids"]
        categories = ProfileCategory.objects.filter(
            id__in=categories_ids, enabled=False, status=CategoryStatus.DELETED.value
        )

        for category in categories:
            # 增加审计日志, 删除同步功能
            post_category_hard_delete.send_robust(
                sender=self, instance=category, operator=request.operator, extra_values={"request": request}
            )
            # 删除人员，部门，关系，目录设置
            hard_delete_category_related_resource.delay(category_id=category.id)

        return Response()
