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

from bkuser.apis.web.data_source.serializers import UserCreateInputSLZ, UserCreateOutputSLZ
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.biz.data_source_organization import (
    DataSourceOrganizationHandler,
    DataSourceUserBaseInfo,
    DataSourceUserRelationInfo,
)
from bkuser.common.error_codes import error_codes


class DataSourceUserListCreateApi(generics.ListCreateAPIView):
    pagination_class = None

    @swagger_auto_schema(
        operation_description="新建数据源用户",
        query_serializer=UserCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: UserCreateOutputSLZ(many=True)},
        tags=["data_source"],
    )
    def post(self, request, *args, **kwargs):
        slz = UserCreateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        data_source_id = kwargs["id"]

        # 校验数据源是否存在
        try:
            data_source = DataSource.objects.get(id=data_source_id)
        except Exception:
            raise error_codes.DATA_SOURCE_NOT_EXIST

        # 不允许对非本地数据源进行用户新增操作
        else:
            if data_source.plugin.id != "local":
                raise error_codes.CANNOT_CREATE_USER

        # 校验是否已存在该用户
        try:
            DataSourceUser.objects.get(
                username=data["username"],
                data_source=data_source,
            )
        except Exception:
            pass

        else:
            raise error_codes.DATA_SOURCE_USER_ALREADY_EXISTED

        # 用户数据整合
        base_user_info = DataSourceUserBaseInfo(
            data_source=data_source,
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
        return Response({"id": user_id})
