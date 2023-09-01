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
from django.db import transaction
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apis.web.data_source import serializers as slzs
from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.data_source.models import DataSource, DataSourceDepartment, DataSourcePlugin, DataSourceUser
from bkuser.apps.data_source.signals import post_create_data_source
from bkuser.biz.data_source_organization import (
    DataSourceOrganizationHandler,
    DataSourceUserBaseInfo,
    DataSourceUserRelationInfo,
)
from bkuser.common.error_codes import error_codes
from bkuser.common.views import ExcludePatchAPIViewMixin


class DataSourcePluginListApi(generics.ListAPIView):
    queryset = DataSourcePlugin.objects.all()
    pagination_class = None
    serializer_class = slzs.DataSourcePluginOutputSLZ

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源插件列表",
        responses={status.HTTP_200_OK: slzs.DataSourcePluginOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DataSourceListCreateApi(CurrentUserTenantMixin, generics.ListCreateAPIView):
    pagination_class = None
    serializer_class = slzs.DataSourceSearchOutputSLZ

    def get_serializer_context(self):
        return {"data_source_plugin_map": dict(DataSourcePlugin.objects.values_list("id", "name"))}

    def get_queryset(self):
        slz = slzs.DataSourceSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        queryset = DataSource.objects.filter(owner_tenant_id=self.get_current_tenant_id())
        if kw := data.get("keyword"):
            queryset = queryset.filter(name__icontains=kw)

        return queryset

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源列表",
        query_serializer=slzs.DataSourceSearchInputSLZ(),
        responses={status.HTTP_200_OK: slzs.DataSourceSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="新建数据源",
        request_body=slzs.DataSourceCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: slzs.DataSourceCreateOutputSLZ()},
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        slz = slzs.DataSourceCreateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        current_user = self.request.user.username
        ds = DataSource.objects.create(
            name=data["name"],
            owner_tenant_id=self.get_current_tenant_id(),
            plugin=DataSourcePlugin.objects.get(id=data["plugin_id"]),
            plugin_config=data["plugin_config"],
            field_mapping=data["field_mapping"],
            creator=current_user,
            updater=current_user,
        )
        # 数据源创建后，发送信号用于登录认证，用户初始化等相关工作
        post_create_data_source.send(sender=self.__class__, data_source=ds)

        return Response(
            slzs.DataSourceCreateOutputSLZ(instance={"id": ds.id}).data,
            status=status.HTTP_201_CREATED,
        )


class DataSourceRetrieveUpdateApi(CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.RetrieveUpdateAPIView):
    pagination_class = None
    serializer_class = slzs.DataSourceRetrieveOutputSLZ
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return DataSource.objects.filter(owner_tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源详情",
        responses={status.HTTP_200_OK: slzs.DataSourceRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="更新数据源",
        request_body=slzs.DataSourceUpdateInputSLZ(),
        responses={status.HTTP_200_OK: ""},
    )
    def put(self, request, *args, **kwargs):
        data_source = self.get_object()
        slz = slzs.DataSourceUpdateInputSLZ(
            data=request.data,
            context={"plugin_id": data_source.plugin_id},
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source.plugin_config = data["plugin_config"]
        data_source.field_mapping = data["field_mapping"]
        data_source.updater = self.request.user.username
        data_source.save()

        return Response()


class DataSourceConnectivityApi(generics.RetrieveAPIView):
    """数据源连通性测试"""

    def get(self, request, *args, **kwargs):
        # TODO 实现代码逻辑
        return Response()


class DataSourceUserListCreateApi(generics.ListCreateAPIView):
    serializer_class = slzs.UserSearchOutputSLZ
    lookup_url_kwarg = "id"

    def get_queryset(self):
        slz = slzs.UserSearchInputSLZ(data=self.request.query_params)
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
        query_serializer=slzs.UserSearchInputSLZ(),
        responses={status.HTTP_200_OK: slzs.UserSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="新建数据源用户",
        request_body=slzs.UserCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: slzs.UserCreateOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        # 校验数据源是否存在
        data_source = DataSource.objects.filter(id=self.kwargs["id"]).first()
        if not data_source:
            raise error_codes.DATA_SOURCE_NOT_EXIST

        slz = slzs.UserCreateInputSLZ(data=request.data, context={"data_source": data_source})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 不允许对非本地数据源进行用户新增操作
        if not data_source.is_local:
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
        return Response(slzs.UserCreateOutputSLZ(instance={"id": user_id}).data)


class DataSourceLeadersListApi(generics.ListAPIView):
    serializer_class = slzs.LeaderSearchOutputSLZ

    def get_queryset(self):
        slz = slzs.LeaderSearchInputSLZ(data=self.request.query_params)
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
        query_serializer=slzs.LeaderSearchInputSLZ(),
        responses={status.HTTP_200_OK: slzs.LeaderSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DataSourceDepartmentsListApi(generics.ListAPIView):
    serializer_class = slzs.DepartmentSearchOutputSLZ

    def get_queryset(self):
        slz = slzs.DepartmentSearchInputSLZ(data=self.request.query_params)
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
        query_serializer=slzs.DepartmentSearchInputSLZ(),
        responses={status.HTTP_200_OK: slzs.DepartmentSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DataSourceUserImportExportApi(generics.ListCreateAPIView):
    """本地数据源用户导入导出"""

    def get(self, request, *args, **kwargs):
        """导出指定的本地数据源用户数据（Excel 格式）"""
        # TODO 实现代码逻辑
        return Response()

    def post(self, request, *args, **kwargs):
        """导入本地数据源用户数据（Excel 格式）"""
        # TODO 实现代码逻辑
        return Response()
