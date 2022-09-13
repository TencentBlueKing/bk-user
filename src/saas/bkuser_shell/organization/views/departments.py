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

from rest_framework.permissions import IsAuthenticated

import bkuser_sdk
from bkuser_global.drf_crown import inject_serializer
from bkuser_shell.apis.viewset import BkUserApiViewSet
from bkuser_shell.bkiam.constants import IAMAction
from bkuser_shell.common.response import Response
from bkuser_shell.organization.serializers.departments import DepartmentListSerializer, ListDepartmentSerializer
from bkuser_shell.proxy.proxy import BkUserApiProxy

logger = logging.getLogger(__name__)


class DepartmentViewSet(BkUserApiViewSet, BkUserApiProxy):

    permission_classes = [
        IsAuthenticated,
    ]

    ACTION_ID = IAMAction.MANAGE_DEPARTMENT.value

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

    def create(self, request, *args, **kwargs):
        """创建组织"""
        return self.do_proxy(request, rewrite_path="/api/v1/web/departments/")
