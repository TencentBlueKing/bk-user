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
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apis.open_v2.mixins import OpenApiAccessControlMixin
from bkuser.apps.data_source.models import DataSourceDepartmentUserRelation, DataSourceUserLeaderRelation


class DepartmentProfileRelationListApi(OpenApiAccessControlMixin, generics.ListAPIView):
    queryset = DataSourceDepartmentUserRelation.objects.all()
    pagination_class = None

    @swagger_auto_schema(
        tags=["open_v2.profiles"],
        operation_description="部门与用户关系表",
        responses={status.HTTP_200_OK: "TODO"},
    )
    def get(self, request, *args, **kwargs):
        return Response("TODO")


class ProfileLeaderRelationListApi(OpenApiAccessControlMixin, generics.ListAPIView):
    queryset = DataSourceUserLeaderRelation.objects.all()
    pagination_class = None

    @swagger_auto_schema(
        tags=["open_v2.profiles"],
        operation_description="用户与 Leader 关系表",
        responses={status.HTTP_200_OK: "TODO"},
    )
    def get(self, request, *args, **kwargs):
        return Response("TODO")
