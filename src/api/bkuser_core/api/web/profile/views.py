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

from .serializers import LoginProfileRetrieveSerializer, LoginProfileSerializer
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
