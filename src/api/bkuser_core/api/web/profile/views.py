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


from rest_framework import generics
from rest_framework.response import Response

from .serializers import (
    LoginProfileRetrieveSerializer,
    LoginProfileSerializer,
    ProfileSearchResultSerializer,
    ProfileSearchSerializer,
)
from bkuser_core.api.web.utils import get_category, get_username
from bkuser_core.api.web.viewset import CustomPagination
from bkuser_core.bkiam.permissions import IAMAction, Permission
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.utils import parse_username_domain


class LoginProfileRetrieveApi(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        slz = LoginProfileRetrieveSerializer(data=request.query_params)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data
        username = data["username"]

        username, domain = parse_username_domain(username)
        if not domain:
            domain = ProfileCategory.objects.get(default=True).domain

        profile = Profile.objects.get(username=username, domain=domain)

        return Response(LoginProfileSerializer(profile).data)


class ProfileSearchApi(generics.ListAPIView):
    serializer_class = ProfileSearchResultSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        serializer = ProfileSearchSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        category_id = data.get("category_id")

        username = get_username(self.request)
        category = get_category(category_id)
        Permission().allow_category_action(username, IAMAction.VIEW_CATEGORY, category)

        queryset = Profile.objects.filter(category_id=category_id, enabled=True)

        if data.get("username"):
            queryset = queryset.filter(username__icontains=data["username"])
        if data.get("display_name"):
            queryset = queryset.filter(display_name__icontains=data["display_name"])
        if data.get("email"):
            queryset = queryset.filter(email__icontains=data["email"])
        if data.get("telephone"):
            queryset = queryset.filter(telephone__icontains=data["telephone"])

        if data.get("status"):
            queryset = queryset.filter(status=data["status"])
        if data.get("staff_status"):
            queryset = queryset.filter(staff_status=data["staff_status"])

        if data.get("departments"):
            queryset = queryset.filter(departments__in=data["departments"])

        # NOTE: 这里相对原来/api/v3/profiles/?category_id 的差异是 enabled=True
        return queryset
