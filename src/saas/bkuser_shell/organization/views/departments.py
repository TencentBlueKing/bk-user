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

import bkuser_sdk
from bkuser_shell.apis.viewset import BkUserApiViewSet
from bkuser_shell.bkiam.constants import IAMAction
from bkuser_shell.common.error_codes import error_codes
from bkuser_shell.common.response import Response
from bkuser_shell.common.serializers import EmptySerializer
from bkuser_shell.organization.serializers.departments import (
    CreateDepartmentSerializer,
    DepartmentAddProfilesSerializer,
    DepartmentListSerializer,
    DepartmentProfileSerializer,
    DepartmentSearchSerializer,
    DepartmentSerializer,
    ListDepartmentSerializer,
    RetrieveDepartmentSLZ,
    UpdateDepartmentSerializer,
)
from bkuser_shell.organization.serializers.profiles import DepartmentGetProfileResultSerializer
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from bkuser_global.drf_crown import ResponseParams, inject_serializer

logger = logging.getLogger(__name__)


class DepartmentViewSet(BkUserApiViewSet):

    permission_classes = [
        IsAuthenticated,
    ]

    ACTION_ID = IAMAction.MANAGE_DEPARTMENT.value

    @inject_serializer(query_in=RetrieveDepartmentSLZ, out=DepartmentSerializer, tag=["departments"])
    def retrieve(self, request, department_id, validated_data):
        api_instance = bkuser_sdk.DepartmentsApi(self.get_api_client_by_request(request, no_auth=True))
        return api_instance.v2_departments_read(department_id, include_disabled=True)

    @staticmethod
    def _get_profiles_count(api_instance, department_id, recursive, page, page_size):
        # 获取当前部门的人员数量
        profiles_response = api_instance.v2_departments_profiles_read(
            department_id,
            recursive=recursive,
            detail=False,
            page=page,
            page_size=page_size,
        )
        return profiles_response.get("count")

    @inject_serializer(
        query_in=DepartmentProfileSerializer, out=DepartmentGetProfileResultSerializer, tags=["departments"]
    )
    def get_profiles(self, request, department_id, validated_data):
        recursive = validated_data.get("recursive", True)
        page = validated_data["page"]
        page_size = validated_data["page_size"]

        request_params = {
            "lookup_value": department_id,
            "recursive": recursive,
            "detail": True,
            "page": page,
            "page_size": page_size,
        }
        if validated_data.get("keyword"):
            request_params["wildcard_search"] = validated_data.get("keyword")

        # 获取当前部门的人员数量
        api_instance = bkuser_sdk.DepartmentsApi(
            self.get_api_client_by_request(request, force_action_id=IAMAction.VIEW_DEPARTMENT.value)
        )
        profiles_response = api_instance.v2_departments_profiles_read(**request_params)

        # 获取自定义字段
        fields_api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request))
        fields = self.get_paging_results(fields_api_instance.v2_dynamic_fields_list)
        extra_fields = [x for x in fields if not x["builtin"]]

        data = {"count": profiles_response.get("count"), "data": profiles_response.get("results")}
        if recursive:
            data["current_count"] = self._get_profiles_count(api_instance, department_id, False, 1, 1)
        else:
            data["total_count"] = self._get_profiles_count(api_instance, department_id, True, 1, 1)

        return ResponseParams(data, {"context": {"fields": extra_fields, "request": request}})

    @inject_serializer(
        query_in=DepartmentListSerializer, out=ListDepartmentSerializer(many=True), tags=["departments"]
    )
    def list(self, request, validated_data):
        """拉取部门信息，按照用户目录分组，默认附带两级子部门信息"""
        # 默认拉取根部门
        profiles_api_instance = bkuser_sdk.ProfilesApi(self.get_api_client_by_request(request, no_auth=True))
        categories_api_instance = bkuser_sdk.CategoriesApi(
            self.get_api_client_by_request(request, force_action_id=IAMAction.MANAGE_CATEGORY.value)
        )
        no_auth_categories_api_instance = bkuser_sdk.CategoriesApi(
            self.get_api_client_by_request(request, no_auth=True)
        )
        departments_api_instance = bkuser_sdk.ShortcutsApi(
            self.get_api_client_by_request(request, force_action_id=IAMAction.VIEW_DEPARTMENT.value)
        )

        only_enabled = validated_data.get("only_enabled")

        # TODO: 简化这种的序列化流程
        # 这里展示两类目录：1. 用户拥有该目录下某个组织的权限 2. 用户拥有这个目录的管理权限

        # 拥有管理权限的目录
        try:
            managed_categories = self.get_paging_results(categories_api_instance.v2_categories_list)
        except Exception:  # pylint: disable=broad-except
            managed_categories = []

        # 拉取所有目录，存在仅对某些部门拥有权限，但是并未拥有目录权限的情况
        all_categories = self.get_paging_results(no_auth_categories_api_instance.v2_categories_list)

        # 默认不展示禁用的目录
        if only_enabled:
            all_categories = [x for x in all_categories if x["enabled"]]
            managed_categories = [x for x in managed_categories if x["enabled"]]

        # 初始化部门人员数量
        def init_departments(x):
            try:
                result = profiles_api_instance.v2_profiles_list(
                    lookup_field="category_id",
                    exact_lookups=[x["id"]],
                    page=1,
                    page_size=1,
                    fields=["id"],
                )

                if result:
                    x["profile_count"] = result.get("count", 0)
                else:
                    x["profile_count"] = 0
            except Exception:  # pylint: disable=broad-except
                logger.exception("fetch profiles count failed. [category_id=%s]", x["id"])
                x["profile_count"] = 0

            x["departments"] = []
            return x

        all_categories = map(init_departments, all_categories)
        all_categories = {x["id"]: x for x in all_categories}
        # 使用 map 减少遍历
        # 此时拥有管理权限的目录已经被加入到了列表
        managed_categories = {x["id"]: all_categories[x["id"]] for x in managed_categories}

        # 这里拉取所有拥有权限的、顶级的目录
        for department in departments_api_instance.v2_shortcuts_departments_list_tops():
            # 如果存在当前可展示的全量 category 未包含的部门，舍弃
            dep_cate_id = department["category_id"]
            if dep_cate_id not in all_categories:
                logger.warning(
                    "department<%s>'s category<%s> could not be found",
                    department["id"],
                    dep_cate_id,
                )
                continue

            # 如果存在没有管理权限的目录，但是其中的组织有权限，在这里会被加进去
            managed_categories[dep_cate_id] = all_categories[dep_cate_id]
            managed_categories[dep_cate_id]["departments"].append(department)

        # 考虑到效率不使用 serializer
        return Response(data=managed_categories.values())

    @inject_serializer(query_in=DepartmentSearchSerializer, out=DepartmentSerializer(many=True), tags=["departments"])
    def search_in_category(self, request, category_id, validated_data):
        """在 category 中查找组织"""
        api_instance = bkuser_sdk.DepartmentsApi(
            self.get_api_client_by_request(request, force_action_id=IAMAction.VIEW_DEPARTMENT.value)
        )
        keyword = validated_data.get("keyword")
        max_items = validated_data.get("max_items")
        hit_departments = api_instance.v2_departments_list(
            page=1,
            page_size=max_items,
            wildcard_search=keyword,
            wildcard_search_fields=["name"],
        )
        departments = [x for x in hit_departments.get("results") if x["category_id"] == int(category_id)]
        return departments

    @inject_serializer(
        body_in=CreateDepartmentSerializer,
        out=DepartmentSerializer,
        config={"default_return_status": status.HTTP_201_CREATED},
        tags=["departments"],
    )
    def create(self, request, validated_data):
        """创建组织"""
        department = bkuser_sdk.Department(**validated_data)
        if not department.parent:
            force_action_id = IAMAction.MANAGE_CATEGORY.value
        else:
            force_action_id = IAMAction.MANAGE_DEPARTMENT.value

        client = self.get_api_client_by_request(request=request, force_action_id=force_action_id)
        api_instance = bkuser_sdk.DepartmentsApi(client)
        department = api_instance.v2_departments_create(body=department)
        return department

    @inject_serializer(body_in=UpdateDepartmentSerializer, out=DepartmentSerializer, tags=["departments"])
    def update(self, request, department_id, validated_data):
        """更新组织名称"""
        body = {"name": validated_data["name"]}
        api_instance = bkuser_sdk.DepartmentsApi(self.get_api_client_by_request(request))
        return api_instance.v2_departments_partial_update(lookup_value=department_id, body=body)

    @inject_serializer(body_in=UpdateDepartmentSerializer, tags=["departments"])
    def switch_order(self, request, department_id, another_department_id, validated_data):
        """更新组织顺序"""
        api_instance = bkuser_sdk.DepartmentsApi(self.get_api_client_by_request(request))

        departments = []
        for x_id in [department_id, another_department_id]:
            departments.append(api_instance.v2_departments_read(x_id))

        # 交换 order 字段
        department_a, department_b = departments
        for index, x_department in enumerate([department_b, department_a]):
            body = {"order": x_department.order}
            api_instance.v2_departments_partial_update(lookup_value=departments[index].id, body=body)

        return Response(data={})

    @inject_serializer(tags=["departments"])
    def delete(self, request, department_id):
        """移除组织"""
        api_instance = bkuser_sdk.DepartmentsApi(self.get_api_client_by_request(request))
        department = api_instance.v2_departments_read(department_id)
        # 当组织存在下级时无法删除
        if department.children:
            raise error_codes.CANNOT_DELETE_DEPARTMENT.f(_("当前部门存在下级组织无法删除"))

        profiles = api_instance.v2_departments_profiles_read(department_id)
        if profiles["results"]:
            raise error_codes.CANNOT_DELETE_DEPARTMENT.f(_("当前部门下存在用户无法删除"))

        api_instance.v2_departments_delete(department_id)
        return Response(data={})

    @inject_serializer(body_in=DepartmentAddProfilesSerializer, out=EmptySerializer, tags=["departments"])
    def add_profiles(self, request, department_id, validated_data):
        api_instance = bkuser_sdk.DepartmentsApi(self.get_api_client_by_request(request))
        api_instance.v2_departments_profiles_create(body=validated_data, lookup_value=department_id)
        return Response(data={})


class DepartmentsApiViewSet(BkUserApiViewSet):
    """用户信息模块"""

    permission_classes = [IsAuthenticated]
    ACTION_ID = IAMAction.MANAGE_DEPARTMENT.value

    def get(self, request, *args, **kwargs):
        return self.call_through_api(request)
