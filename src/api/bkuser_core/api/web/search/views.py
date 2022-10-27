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
from collections.abc import Iterable
from typing import Dict, List

from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import generics
from rest_framework.response import Response

from .serializers import (
    SearchInputSLZ,
    SearchResultDepartmentOutputSLZ,
    SearchResultOutputSLZ,
    SearchResultProfileOutputSLZ,
)
from bkuser_core.api.web.utils import get_operator
from bkuser_core.bkiam.exceptions import IAMPermissionDenied
from bkuser_core.bkiam.permissions import IAMAction, Permission
from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import DynamicFieldInfo, Profile

# from collections import defaultdict


logger = logging.getLogger(__name__)


class SearchApi(generics.ListAPIView):
    serializer_class = SearchResultOutputSLZ

    def get_profile_field_name(self, field) -> str:
        return {
            "email": _("邮箱"),
            "qq": _("QQ"),
            "display_name": _("全名"),
            "telephone": _("手机号"),
            "extras": _("自定义字段"),
            "username": _("用户名"),
        }.get(field, field)

    def _search_profiles(self, operator: str, keyword: str, max_items: int) -> List[Dict]:
        results = []
        try:
            dept_ft_for_profile = Permission().make_filter_of_department(operator, IAMAction.MANAGE_DEPARTMENT)
            logger.info("global search `%s`, make a filter for profile: %s", keyword, dept_ft_for_profile)
        except IAMPermissionDenied as e:
            logger.warning("user %s has no permission to search profiles in department", operator)
            raise e
        else:
            profile_qs = Profile.objects.filter(
                Q(username__icontains=keyword)
                | Q(display_name__icontains=keyword)
                | Q(email__icontains=keyword)
                | Q(telephone__icontains=keyword)
                | Q(qq__icontains=keyword)
                | Q(extras__icontains=keyword)
            )
            if dept_ft_for_profile:
                profile_qs = profile_qs.filter(dept_ft_for_profile)

            profiles = profile_qs.all()[:max_items]

            # NOTE: 先兼容目前前端需要的空数据结构
            profile_result: Dict[str, List] = {
                "username": [],
                "display_name": [],
                "email": [],
                "telephone": [],
                "qq": [],
                "extras": [],
            }

            extra_fields = DynamicFieldInfo.objects.filter(enabled=True, builtin=False).values("name", "display_name")
            extra_field_display_name_map = {f["name"]: f["display_name"] for f in extra_fields}

            for profile in profiles:
                if keyword in profile.email:
                    profile_result["email"].append(profile)
                    continue
                if keyword in profile.username:
                    profile_result["username"].append(profile)
                    continue
                if keyword in profile.display_name:
                    profile_result["display_name"].append(profile)
                    continue
                if keyword in profile.telephone:
                    profile_result["telephone"].append(profile)
                    continue
                if keyword in profile.qq:
                    profile_result["qq"].append(profile)
                    continue

                for k, v in profile.extras.items():
                    if not v:
                        continue
                    if not isinstance(v, Iterable):
                        continue
                    if keyword in v:
                        # 这里如果没有拿到, 意味着extras对应字段已经被删除/禁用但是用户数据里面还有, 所以过滤掉这种结果
                        hit_extra_display_name = extra_field_display_name_map.get(k)
                        if hit_extra_display_name:
                            # 这个字段用于前端搜索结果展示: 命中的哪个字段
                            profile.hit_extra_display_name = hit_extra_display_name
                            profile_result["extras"].append(profile)

            for key, items in profile_result.items():
                results.append(
                    {
                        "type": key,
                        "display_name": self.get_profile_field_name(key),
                        "items": SearchResultProfileOutputSLZ(items, many=True).data,
                    }
                )

        return results

    def _search_departments(self, operator: str, keyword: str, max_items: int) -> List[Dict]:
        results = []
        try:
            dept_ft = Permission().make_department_filter(operator, IAMAction.MANAGE_DEPARTMENT)
            logger.info("global search `%s`, make a filter for department: %s", keyword, dept_ft)
        except IAMPermissionDenied as e:
            logger.warning("user %s has no permission to search department", operator)
            raise e
        else:
            department_qs = Department.objects.filter(
                name__icontains=keyword,
            )
            if dept_ft:
                department_qs = department_qs.filter(dept_ft)

            departments = department_qs.all()[:max_items]
            if departments:
                results.append(
                    {
                        "type": "department",
                        "display_name": _("组织"),
                        "items": SearchResultDepartmentOutputSLZ(departments, many=True).data,
                    }
                )

        return results

    def get(self, request, *args, **kwargs):
        operator = get_operator(self.request)

        slz = SearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        max_items = data.get("max_items", 20)
        # NOTE: 防御
        if max_items >= 100:
            max_items = 100
        keyword = data["keyword"]
        if not keyword:
            return Response(data=[])

        result = []

        # NOTE: include disabled!
        result.extend(self._search_profiles(operator, keyword, max_items))
        result.extend(self._search_departments(operator, keyword, max_items))

        return Response(SearchResultOutputSLZ(result, many=True).data)
