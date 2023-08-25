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

from bkuser.apis.web.data_source.serializers import (
    UserCreateInputSLZ,
    UserCreateOutputSLZ,
    UserSearchInputSLZ,
    UserSearchOutputSLZ,
)
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.biz.data_source_organization import (
    DataSourceOrganizationHandler,
    DataSourceUserBaseInfo,
    DataSourceUserRelationInfo,
)
from bkuser.common.error_codes import error_codes


class DataSourceUserListCreateApi(generics.ListCreateAPIView):
    queryset = DataSource.objects.all()
    pagination_class = None
    serializer_class = UserSearchOutputSLZ
    lookup_url_kwarg = "id"

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

        if data.get("username"):
            queryset = DataSourceUser.objects.filter(username__icontains=data["username"])

        return queryset

    @swagger_auto_schema(
        operation_description="数据源用户列表",
        query_serializer=UserSearchInputSLZ(),
        responses={status.HTTP_200_OK: UserSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="新建数据源用户",
        request_body=UserCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: UserCreateOutputSLZ()},
        tags=["data_source"],
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
        if not data_source.editable:
            raise error_codes.CANNOT_CREATE_USER
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
        )

        relation_info = DataSourceUserRelationInfo(
            department_ids=data["department_ids"], leader_ids=data["leader_ids"]
        )

        user_id = DataSourceOrganizationHandler.create_user(
            data_source=data_source, base_user_info=base_user_info, relation_info=relation_info
        )
        return Response(UserCreateOutputSLZ(instance={"id": user_id}).data)
