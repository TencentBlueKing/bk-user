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
from collections import defaultdict

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
from bkuser_core.api.web.utils import get_username
from bkuser_core.bkiam.exceptions import IAMPermissionDenied
from bkuser_core.bkiam.permissions import IAMAction, Permission
from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import Profile

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

    def get(self, request, *args, **kwargs):
        operator = get_username(self.request)

        serializer = SearchInputSLZ(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        max_items = data.get("max_items", 20)
        # NOTE: 防御
        if max_items >= 100:
            max_items = 100
        keyword = data["keyword"]
        if not keyword:
            return Response(data=[])

        result = []

        # NOTE: include disabled!
        try:
            dept_ft_for_profile = Permission().make_filter_of_department(operator, IAMAction.MANAGE_DEPARTMENT)
            logger.info("global search `%s`, make a filter for profile: %s", keyword, dept_ft_for_profile)
        except IAMPermissionDenied:
            logger.warning("user %s has no permission to search department", operator)
        else:
            profiles = (
                Profile.objects.filter(
                    Q(username__icontains=keyword)
                    | Q(display_name__icontains=keyword)
                    | Q(email__icontains=keyword)
                    | Q(telephone__icontains=keyword)
                    | Q(qq__icontains=keyword)
                    | Q(extras__icontains=keyword)
                )
                .filter(dept_ft_for_profile)
                .all()[:max_items]
            )

            # FIXME: refactor it, now it works
            profile_result = defaultdict(list)
            for profile in profiles:
                if keyword in profile.username:
                    profile_result["username"].append(profile)
                    continue
                if keyword in profile.display_name:
                    profile_result["display_name"].append(profile)
                    continue
                if keyword in profile.email:
                    profile_result["email"].append(profile)
                    continue
                if keyword in profile.telephone:
                    profile_result["telephone"].append(profile)
                    continue
                if keyword in profile.qq:
                    profile_result["qq"].append(profile)
                    continue
                if keyword in profile.extras:
                    profile_result["extras"].append(profile)
                    continue

            for key, items in profile_result.items():
                result.append(
                    {
                        "type": key,
                        "display_name": self.get_profile_field_name(key),
                        "items": SearchResultProfileOutputSLZ(items, many=True).data,
                    }
                )
        # FIXME: make a permission IAMFilter?
        try:
            dept_ft = Permission().make_department_filter(operator, IAMAction.MANAGE_DEPARTMENT)
            logger.info("global search `%s`, make a filter for department: %s", keyword, dept_ft)
        except IAMPermissionDenied:
            logger.warning("user %s has no permission to search department", operator)
        else:
            departments = (
                Department.objects.filter(
                    name__icontains=keyword,
                )
                .filter(dept_ft)
                .all()[:max_items]
            )
            if departments:
                result.append(
                    {
                        "type": "department",
                        "display_name": _("组织"),
                        "items": SearchResultDepartmentOutputSLZ(departments, many=True).data,
                    }
                )
        return Response(SearchResultOutputSLZ(result, many=True).data)
