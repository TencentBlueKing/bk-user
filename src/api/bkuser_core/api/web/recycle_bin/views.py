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
from bkuser_core.api.web.utils import get_category_display_name_map
from bkuser_core.api.web.viewset import CustomPagination
from bkuser_core.categories.constants import CategoryStatus
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.categories.signals import post_category_hard_delete, post_category_revert
from bkuser_core.departments.models import Department, DepartmentThroughModel
from bkuser_core.profiles.constants import ProfileStatus
from bkuser_core.profiles.models import LeaderThroughModel, Profile
from bkuser_core.recycle_bin.constants import RecycleBinObjectType
from bkuser_core.recycle_bin.models import RecycleBin
from bkuser_core.user_settings.models import Setting

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
    serializer_class = CategoryRevertCheckResultOutputSlZ

    def post(self, request, *args, **kwargs):
        input_slz = BatchCategoryRevertInputSlZ(data=request.data)
        input_slz.is_valid(raise_exception=True)
        data = input_slz.validated_data

        # 待还原，需进行检查的软删除目录
        deleted_category_ids = data["deleted_category_ids"]
        deleted_categories = ProfileCategory.objects.filter(
            id__in=deleted_category_ids, enabled=False, status=CategoryStatus.DELETED.value
        )
        if not deleted_categories:
            return Response()

        # 当前使能的目录（停用/启用中的目录）
        enabled_categories = ProfileCategory.objects.filter(enabled=True)
        category_display_name_list = enabled_categories.values_list("display_name", flat=True)

        # 获取当前使能的mad/ldap 的连接域
        enabled_connection_url_list = Setting.objects.filter(
            category_id__in=enabled_categories.values_list("id", flat=True), meta__key="connection_url"
        ).values_list("value", flat=True)

        # 提前暴露 待还原 mad/ldap目录的connection_url
        deleted_categories_connection_url = Setting.objects.filter(
            category_id__in=deleted_category_ids, meta__key="connection_url"
        ).values("category_id", "value")
        deleted_category_urls_map: dict = {}
        for item in deleted_categories_connection_url:
            deleted_category_urls_map[item["category_id"]] = item["value"]

        # 开始检查
        check_result_list: list = []
        for del_category in deleted_categories:
            # 检查结果初始化
            check_detail: dict = {
                "category_id": del_category.id,
                "category_display_name": del_category.display_name,
                "check_status": True,
                "error_message": "",
            }

            # 重名检测
            if del_category.display_name in category_display_name_list:
                check_detail["check_status"] = False
                check_detail["error_message"] = CategoryCheckMessageEnum.REPEATED_DISPLAY_NAME.value
                check_result_list.append(check_detail)
                continue

            # 连接域检查, connection_url=None 不是local就是未配置完全的ldap/mad
            connection_url = deleted_category_urls_map.get(del_category.id, None)
            if connection_url and connection_url in enabled_connection_url_list:
                check_detail["check_status"] = False
                check_detail["error_message"] = CategoryCheckMessageEnum.REPEATED_CONNECTION_URL.value
                check_result_list.append(check_detail)
                continue

            check_result_list.append(check_detail)

        return Response(data=self.serializer_class(instance=check_result_list, many=True).data)


class RecycleBinBatchCategoryRevertApi(generics.CreateAPIView):
    queryset = RecycleBin.objects.filter(object_type=RecycleBinObjectType.CATEGORY.value)
    serializer_class = CategoryRevertResultOutputSlZ

    def post(self, request, *args, **kwargs):
        input_slz = BatchCategoryRevertInputSlZ(data=request.data)
        input_slz.is_valid(raise_exception=True)
        data = input_slz.validated_data

        # 还原软删除目录状态
        reverting_category_ids = data["deleted_category_ids"]
        reverting_categories = ProfileCategory.objects.filter(
            id__in=reverting_category_ids, enabled=False, status=ProfileStatus.DELETED.value
        )

        # 当前使能的目录（停用/启用中的目录）
        enabled_categories = ProfileCategory.objects.filter(enabled=True)
        enabled_category_display_names = enabled_categories.values_list("display_name", flat=True)

        # 获取当前使能的mad/ldap 的连接域
        enabled_categories_connection_urls = Setting.objects.filter(
            category_id__in=enabled_categories.values_list("id", flat=True), meta__key="connection_url"
        ).values_list("value", flat=True)

        # 提前暴露待还原 mad/ldap目录的connection_url
        reverting_categories_connection_settings = Setting.objects.filter(
            category_id__in=reverting_category_ids, meta__key="connection_url"
        ).values("category_id", "value")
        reverting_category_urls: dict = {}
        for item in reverting_categories_connection_settings:
            reverting_category_urls[item["category_id"]] = item["value"]

        # 还原结果初始化
        revert_results: dict = {
            "successful_count": 0,
            "failed_count": 0,
        }
        # 成功还原的目录id
        reverted_category_ids: list = []

        for category in reverting_categories:
            # 二次检查
            # 避免还原过程中，同名目录出现
            if category.display_name in enabled_category_display_names:
                logger.error(
                    "Category<%s-%s> get a repeated display_name<%s>",
                    category.id,
                    category.display_name,
                    category.display_name,
                )
                revert_results["failed_count"] += 1
                continue

            # 获取不到则可能是未配置，或者为本地目录
            connection_url = reverting_category_urls.get(category.id, None)
            if connection_url and connection_url in enabled_categories_connection_urls:
                logger.error(
                    "Category<%s-%s> get a repeated connection url<%s>",
                    category.id,
                    category.display_name,
                    category.display_name,
                )
                revert_results["failed_count"] += 1
                continue

            category.revert()
            # 善后: 恢复原本的定时任务，增加审计日志
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
        slz = BatchCategoryHardDeleteInputSlZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 删除关联资源
        categories_ids = data["category_ids"].split(",")
        with transaction.atomic():
            categories = ProfileCategory.objects.filter(id__in=categories_ids)

            # 上下级关系删除
            logger.info("Categories %s: clear leaders and profiles' relationship.", categories_ids)
            relate_profiles = Profile.objects.filter(category_id__in=categories_ids)
            LeaderThroughModel.objects.filter(from_profile_id__in=relate_profiles).delete()

            # 人员-部门关系删除
            logger.info("Categories %s: clear departments and profiles' relationship", categories_ids)
            relate_departments = Department.objects.filter(category_id__in=categories_ids)
            DepartmentThroughModel.objects.filter(
                department_id__in=relate_departments.values_list("id", flat=True)
            ).delete()

            # 清理资源: 人员，部门，目录设置
            logger.info("Categories: clear departments, profiles and settings ", categories_ids)
            Setting.objects.filter(category_id__in=categories_ids).delete()
            relate_departments.delete()
            relate_profiles.delete()

            # 删除回收站记录
            self.queryset.filter(object_id__in=categories_ids).delete()

            # 善后，删除定时任务，增加审计日志
            [
                post_category_hard_delete.send_robust(
                    sender=self, instance=instance, operator=request.operator, extra_values={"request": request}
                )
                for instance in categories
            ]

            # 删除目录
            categories.delete()

        return Response()
