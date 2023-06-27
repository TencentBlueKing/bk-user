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
from typing import Any, Dict

from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import CategoryOutputSLZ
from bkuser_core.api.web.utils import get_operator, is_filter_means_any
from bkuser_core.bkiam.exceptions import IAMPermissionDenied
from bkuser_core.bkiam.permissions import IAMAction, Permission
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import Profile

logger = logging.getLogger(__name__)


class HomeTreeListApi(generics.ListCreateAPIView):
    def _get_categories(self, operator):
        # TODO: 组织架构+目录 合并后, 需要展示未启用的目录
        # 拥有管理权限的目录
        try:
            queryset = ProfileCategory.objects.filter(enabled=True)
            if settings.ENABLE_IAM:
                fs = Permission().make_category_filter(operator, IAMAction.VIEW_CATEGORY)
                queryset = queryset.filter(fs)
            managed_categories = queryset.all()
        except IAMPermissionDenied:
            managed_categories = []
        except Exception as e:
            raise e

        # 拉取所有目录，存在仅对某些部门拥有权限，但是并未拥有目录权限的情况
        all_categories = ProfileCategory.objects.filter(enabled=True).all()

        return managed_categories, all_categories

    def _get_category_profile_count(self, category_id) -> int:
        return Profile.objects.filter(enabled=True, category_id=category_id).count()

    def _list_department_tops(self, operator):
        """获取最顶层的组织列表[权限中心亲和]"""
        # NOTE: 不能用values/values_list, 后面mptt has_children需要一个完整的model
        # 这些字段不查询, speed up 200ms for 6000 departments
        defer_fields = ["create_time", "update_time", "code", "extras", "enabled"]
        # TODO: enabled should be ignored too?

        if not settings.ENABLE_IAM:
            return Department.objects.filter(level=0, enabled=True).all().defer(*defer_fields)

        try:
            dept_ft = Permission().make_department_filter(operator, IAMAction.MANAGE_DEPARTMENT)
            logger.debug("list_department_tops, make a filter for department: %s", dept_ft)
        except IAMPermissionDenied as e:
            logger.warning("user %s has no permission to search department", operator)
            raise e
        else:
            # 如果是any, 表示有所有一级department的权限, 直接返回
            if is_filter_means_any(dept_ft):
                return Department.objects.filter(level=0, enabled=True).all().defer(*defer_fields)

            # 1. 拿到权限中心里授过权的全列表
            queryset = Department.objects.filter(enabled=True).filter(dept_ft)
            # 没有任何权限, 返回空
            if not queryset:
                return []

            # ref: https://github.com/TencentBlueKing/bk-user/issues/641#issuecomment-1248845995
            # 原始方案: 如果父节点已经授过权，剔除子节点(这里是原先的查询, 暂时保持不变) => 全表扫描
            # descendants = Department.tree_objects.get_queryset_descendants(queryset=queryset, include_self=False)
            # queryset = queryset.exclude(id__in=descendants.values_list("id", flat=True))
            # logger.info("1 result: %s", list(queryset.all()))

            # replace 方案 1 => 获取祖先+level=0, 全表扫描
            # queryset = Department.tree_objects.get_queryset_ancestors(queryset=queryset, include_self=True).filter(
            #     level=0
            # )
            # logger.info("2 result: %s", list(queryset.all()))

            # replace 方案 2 => 直接拿获取到的部门的 instance.get_root() => 使用tree_id+parent_id判定 => 加索引
            # - 获取有权限部门所在的tree_id, 并去重
            has_permission_depts = list(set(queryset.values_list("tree_id", flat=True)))
            # SQL: WHERE (`parent_id` IS NULL AND `tree_id` IN (1, 2, 4, 5, 6, 7))
            queryset = Department.tree_objects._mptt_filter(
                tree_id__in=has_permission_depts, parent=None, enabled=True
            )
            # logger.info("3 result: %s", list(queryset.all()))

            # FIXME: 这里为空抛异常? 让用户申请权限? 还是什么都不做
            # if not queryset:
            #     raise IAMPermissionDenied(
            #         detail=_("您没有该操作的权限，请在权限中心申请"),
            #         extra_info=IAMPermissionExtraInfo.from_request(request).to_dict(),
            #     )

            # FIXME: 这里为什么没有限制level=0?
            return queryset.all().defer(*defer_fields)

    def _serialize_department(self, dept: Department) -> Dict[str, Any]:
        # better performance
        return {
            "id": dept.id,
            "name": dept.name,
            "order": dept.order,
            "has_children": dept.has_children,
            # "category_id": dept.category_id,
        }

    def _serialize_category(self, category: Dict[str, Any]) -> Dict[str, Any]:
        # better performance
        return {
            "id": category["id"],
            "display_name": category["display_name"],
            "order": category["order"],
            "default": category["default"],
            "type": category["type"],
            "profile_count": category["profile_count"],
            "departments": category["departments"],
            "domain": category["domain"],
            "create_time": category["create_time"],
            "update_time": category["update_time"],
            "configured": category["configured"],
            # "unfilled_namespaces": category["unfilled_namespaces"],
            "activated": category["activated"],
            "syncing": category["syncing"],
            # NOT IN: enabled/description/last_synced_time
        }

    def get(self, request, *args, **kwargs):
        # NOTE: 差异点, 也不支持level
        # level = data.get("level")
        # NOTE: 差异点: 不支持only_enabled
        # only_enabled = data.get("only_enabled", True)

        operator = get_operator(self.request)
        # categories
        managed_categories, all_categories = self._get_categories(operator)

        # TODO: 简化这种的序列化流程
        # 这里展示两类目录：1. 用户拥有该目录下某个组织的权限 2. 用户拥有这个目录的管理权限
        all_categories_map = {x.id: CategoryOutputSLZ(x).data for x in all_categories}

        for category_id, c in all_categories_map.items():
            c["profile_count"] = self._get_category_profile_count(category_id)
            c["departments"] = []

        # 此时拥有管理权限的目录已经被加入到了列表
        managed_categories_map = {x.id: all_categories_map[x.id] for x in managed_categories}

        # FIXME: 如果有所有部门的权限, 这里返回的是所有部门? 还是只返回一级部门? 一级部门很多的时候怎么处理?
        # 这里拉取所有拥有权限的、顶级的目录
        for department in self._list_department_tops(operator):
            # 如果存在当前可展示的全量 category 未包含的部门，舍弃
            dept_cate_id = department.category_id
            if dept_cate_id not in all_categories_map:
                logger.warning(
                    "department<%s>'s category<%s> could not be found",
                    department.id,
                    dept_cate_id,
                )
                continue

            # 如果存在没有管理权限的目录，但是其中的组织有权限，在这里会被加进去
            if dept_cate_id not in managed_categories_map:
                # 如果目录的状态正常, 则加入到列表中(防止没管理权限的目录被展示到`不可用的目录`, 用户进行操作)
                # 即, 停用和未配置完成 + 没有管理权限的目录不会被展示
                cat = all_categories_map[dept_cate_id]
                if cat["activated"] and cat["configured"]:
                    managed_categories_map[dept_cate_id] = cat

            managed_categories_map[dept_cate_id]["departments"].append(self._serialize_department(department))

        data = []
        # sort by order, then do serialize and append
        for category in managed_categories_map.values():
            category["departments"].sort(key=lambda x: x["order"])

            data.append(self._serialize_category(category))

        return Response(
            data=data,
            status=status.HTTP_200_OK,
        )
