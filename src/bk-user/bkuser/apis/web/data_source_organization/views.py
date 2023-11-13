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
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.data_source_organization.serializers import (
    DepartmentSearchInputSLZ,
    DepartmentSearchOutputSLZ,
    LeaderSearchInputSLZ,
    LeaderSearchOutputSLZ,
    UserCreateInputSLZ,
    UserCreateOutputSLZ,
    UserRetrieveOutputSLZ,
    UserSearchInputSLZ,
    UserSearchOutputSLZ,
    UserUpdateInputSLZ,
)
from bkuser.apps.data_source.models import DataSource, DataSourceDepartment, DataSourceUser
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.biz.data_source_organization import (
    DataSourceOrganizationHandler,
    DataSourceUserBaseInfo,
    DataSourceUserEditableBaseInfo,
    DataSourceUserRelationInfo,
)
from bkuser.common.error_codes import error_codes
from bkuser.common.views import ExcludePatchAPIViewMixin


class DataSourceUserListCreateApi(generics.ListCreateAPIView):
    serializer_class = UserSearchOutputSLZ
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    def get_queryset(self):
        slz = UserSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        data_source_id = self.kwargs["id"]

        # 校验数据源是否存在
        data_source = DataSource.objects.filter(id=data_source_id).first()
        if not data_source:
            raise error_codes.DATA_SOURCE_NOT_EXIST

        queryset = DataSourceUser.objects.filter(data_source=data_source)
        if username := data.get("username"):
            queryset = queryset.filter(username__icontains=username)

        return queryset

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源用户列表",
        query_serializer=UserSearchInputSLZ(),
        responses={status.HTTP_200_OK: UserSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="新建数据源用户",
        request_body=UserCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: UserCreateOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        # 校验数据源是否存在
        data_source = DataSource.objects.filter(id=self.kwargs["id"]).first()
        if not data_source:
            raise error_codes.DATA_SOURCE_NOT_EXIST

        slz = UserCreateInputSLZ(data=request.data, context={"data_source": data_source})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 不允许对非本地数据源进行用户新增操作
        if not data_source.is_local:
            raise error_codes.CANNOT_CREATE_DATA_SOURCE_USER
        # 校验是否已存在该用户
        if DataSourceUser.objects.filter(username=data["username"], data_source=data_source).exists():
            raise error_codes.DATA_SOURCE_USER_ALREADY_EXISTED

        # 用户数据整合
        base_user_info = DataSourceUserBaseInfo(
            username=data["username"],
            full_name=data["full_name"],
            email=data["email"],
            phone=data["phone"],
            phone_country_code=data["phone_country_code"],
            logo=data["logo"],
        )

        relation_info = DataSourceUserRelationInfo(
            department_ids=data["department_ids"], leader_ids=data["leader_ids"]
        )

        user_id = DataSourceOrganizationHandler.create_user(
            data_source=data_source, base_user_info=base_user_info, relation_info=relation_info
        )
        return Response(UserCreateOutputSLZ(instance={"id": user_id}).data)


class DataSourceLeadersListApi(generics.ListAPIView):
    serializer_class = LeaderSearchOutputSLZ
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    def get_queryset(self):
        slz = LeaderSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 校验数据源是否存在
        data_source = DataSource.objects.filter(id=self.kwargs["id"]).first()
        if not data_source:
            raise error_codes.DATA_SOURCE_NOT_EXIST

        queryset = DataSourceUser.objects.filter(data_source=data_source)
        if keyword := data.get("keyword"):
            queryset = queryset.filter(Q(username__icontains=keyword) | Q(full_name__icontains=keyword))

        return queryset

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源用户上级列表",
        query_serializer=LeaderSearchInputSLZ(),
        responses={status.HTTP_200_OK: LeaderSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DataSourceDepartmentsListApi(generics.ListAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
    serializer_class = DepartmentSearchOutputSLZ

    def get_queryset(self):
        slz = DepartmentSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 校验数据源是否存在
        data_source = DataSource.objects.filter(id=self.kwargs["id"]).first()
        if not data_source:
            raise error_codes.DATA_SOURCE_NOT_EXIST

        queryset = DataSourceDepartment.objects.filter(data_source=data_source)

        if name := data.get("name"):
            queryset = queryset.filter(name__icontains=name)

        return queryset

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源部门列表",
        query_serializer=DepartmentSearchInputSLZ(),
        responses={status.HTTP_200_OK: DepartmentSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DataSourceUserRetrieveUpdateApi(ExcludePatchAPIViewMixin, generics.RetrieveUpdateAPIView):
    queryset = DataSourceUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
    serializer_class = UserRetrieveOutputSLZ

    def get_serializer_context(self):
        user_departments_map = DataSourceOrganizationHandler.get_user_departments_map_by_user_id(
            user_ids=[self.kwargs["id"]]
        )
        user_leaders_map = DataSourceOrganizationHandler.get_user_leaders_map_by_user_id([self.kwargs["id"]])
        return {"user_departments_map": user_departments_map, "user_leaders_map": user_leaders_map}

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源用户详情",
        responses={status.HTTP_200_OK: UserRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="更新数据源用户",
        request_body=UserUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        user = self.get_object()
        if not user.data_source.is_local:
            raise error_codes.CANNOT_UPDATE_DATA_SOURCE_USER

        slz = UserUpdateInputSLZ(data=request.data, context={"data_source": user.data_source, "user_id": user.id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 用户数据整合
        base_user_info = DataSourceUserEditableBaseInfo(
            full_name=data["full_name"],
            email=data["email"],
            phone_country_code=data["phone_country_code"],
            phone=data["phone"],
            logo=data["logo"],
        )
        relation_info = DataSourceUserRelationInfo(
            department_ids=data["department_ids"], leader_ids=data["leader_ids"]
        )
        DataSourceOrganizationHandler.update_user(
            user=user, base_user_info=base_user_info, relation_info=relation_info
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
