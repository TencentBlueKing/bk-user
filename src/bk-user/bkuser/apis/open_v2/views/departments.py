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

from bkuser.apps.tenant.models import TenantDepartment


class DepartmentListApi(generics.ListAPIView):
    queryset = TenantDepartment.objects.all()
    pagination_class = None

    @swagger_auto_schema(
        tags=["open_v2.departments"],
        operation_description="查询部门列表",
        responses={status.HTTP_200_OK: "TODO"},
    )
    def get(self, request, *args, **kwargs):
        return Response("TODO")


class DepartmentRetrieveApi(generics.RetrieveAPIView):
    queryset = TenantDepartment.objects.all()

    @swagger_auto_schema(
        tags=["open_v2.departments"],
        operation_description="查询单个部门信息",
        responses={status.HTTP_200_OK: "TODO"},
    )
    def get(self, request, *args, **kwargs):
        return Response("TODO")


class DepartmentChildrenListApi(generics.ListAPIView):
    queryset = TenantDepartment.objects.all()
    pagination_class = None

    @swagger_auto_schema(
        tags=["open_v2.departments"],
        operation_description="查询子部门列表",
        responses={status.HTTP_200_OK: "TODO"},
    )
    def get(self, request, *args, **kwargs):
        return Response("TODO")


class ProfileDepartmentListApi(generics.ListAPIView):
    queryset = TenantDepartment.objects.all()
    pagination_class = None

    @swagger_auto_schema(
        tags=["open_v2.departments"],
        operation_description="查询单个用户的部门列表",
        responses={status.HTTP_200_OK: "TODO"},
    )
    def get(self, request, *args, **kwargs):
        return Response("TODO")
