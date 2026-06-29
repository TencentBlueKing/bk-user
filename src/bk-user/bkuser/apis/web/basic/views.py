# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apps.permission.permissions import get_user_role
from bkuser.apps.tenant.language import get_supported_language_choices

from .serializers import CurrentUserRetrieveOutputSLZ, SupportedLanguageOutputSLZ


class CurrentUserRetrieveApi(generics.RetrieveAPIView):
    @swagger_auto_schema(
        operation_description="当前用户信息",
        responses={status.HTTP_200_OK: CurrentUserRetrieveOutputSLZ()},
        tags=["basic.current_user"],
    )
    def get(self, request, *args, **kwargs):
        # FIXME: 待新版登录后重构，return更多信息
        current_user = request.user
        current_tenant_id = current_user.get_property("tenant_id")

        info = {
            "username": current_user.username,
            "tenant_id": current_tenant_id,
            "role": get_user_role(current_tenant_id, current_user.username),
            "display_name": current_user.get_property("display_name"),
            "time_zone": current_user.get_property("time_zone"),
            "language": current_user.get_property("language"),
        }

        return Response(CurrentUserRetrieveOutputSLZ(instance=info).data)


class SupportedLanguageListApi(generics.ListAPIView):
    pagination_class = None

    @swagger_auto_schema(
        operation_description="获取支持的语言列表",
        responses={status.HTTP_200_OK: SupportedLanguageOutputSLZ(many=True)},
        tags=["basic.supported_languages"],
    )
    def get(self, request, *args, **kwargs):
        languages = [{"code": code, "name": name} for code, name in get_supported_language_choices()]
        return Response(SupportedLanguageOutputSLZ(languages, many=True).data)
