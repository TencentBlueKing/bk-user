# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apps.permission.permissions import get_user_role
from bkuser.common.constants import TIME_ZONE_CHOICES, BkLanguageEnum

from .serializers import CurrentUserRetrieveOutputSLZ, LanguagesTimeZoneListOutputSLZ


class CurrentUserRetrieveApi(generics.RetrieveAPIView):
    @swagger_auto_schema(
        operation_description="当前用户信息",
        responses={status.HTTP_200_OK: CurrentUserRetrieveOutputSLZ()},
        tags=["basic"],
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
        }

        return Response(CurrentUserRetrieveOutputSLZ(instance=info).data)


class LanguagesListApi(generics.ListAPIView):
    pagination_class = None

    @swagger_auto_schema(
        operation_description="所有语言信息",
        responses={status.HTTP_200_OK: LanguagesTimeZoneListOutputSLZ()},
        tags=["basic"],
    )
    def get(self, request, *args, **kwargs):
        languages = {"中文": BkLanguageEnum.ZH_CN.value, "English": BkLanguageEnum.EN.value}
        languages_list = [{"key": key, "value": value} for key, value in languages.items()]
        return Response(LanguagesTimeZoneListOutputSLZ(languages_list, many=True).data)


class TimeZonesListApi(generics.GenericAPIView):
    pagination_class = None

    @swagger_auto_schema(
        operation_description="所有时区信息",
        responses={status.HTTP_200_OK: LanguagesTimeZoneListOutputSLZ()},
        tags=["basic"],
    )
    def get(self, request, *args, **kwargs):
        timezones = dict(TIME_ZONE_CHOICES)
        time_zones_list = [{"key": key, "value": value} for key, value in timezones.items()]
        return Response(LanguagesTimeZoneListOutputSLZ(time_zones_list, many=True).data)
