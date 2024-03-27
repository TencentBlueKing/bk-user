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
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.models import Tenant
from bkuser.biz.data_source_organization import DataSourceUserHandler
from bkuser.common.views import ExcludePatchAPIViewMixin
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

from .serializers import (
    TenantBuiltinManagerPasswordUpdateInputSLZ,
    TenantBuiltinManagerRetrieveOutputSLZ,
    TenantBuiltinManagerUpdateInputSLZ,
    TenantRetrieveOutputSLZ,
    TenantUpdateInputSLZ,
)


class TenantRetrieveUpdateApi(CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["tenant_info"],
        operation_description="租户详情",
        responses={status.HTTP_200_OK: TenantRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant = Tenant.objects.get(id=self.get_current_tenant_id())
        return Response(TenantRetrieveOutputSLZ(tenant).data)

    @swagger_auto_schema(
        tags=["tenant_info"],
        operation_description="更新租户",
        request_body=TenantUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        tenant = Tenant.objects.get(id=self.get_current_tenant_id())
        slz = TenantUpdateInputSLZ(data=request.data, context={"tenant_id": tenant.id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 更新
        tenant.name = data["name"]
        tenant.logo = data["logo"]
        tenant.visible = data["visible"]
        tenant.user_number_visible = data["user_number_visible"]
        tenant.updater = request.user.username
        tenant.updated_at = timezone.now()
        tenant.save(update_fields=["name", "logo", "updater", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantBuiltinManagerRetrieveUpdateApi(
    CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.RetrieveUpdateAPIView
):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["tenant_info"],
        operation_description="租户内置管理账号信息",
        responses={status.HTTP_200_OK: TenantBuiltinManagerRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        # 查询租户的内置管理数据源
        data_source = DataSource.objects.get(
            owner_tenant_id=self.get_current_tenant_id(), type=DataSourceTypeEnum.BUILTIN_MANAGEMENT
        )
        # 查询内置管理账号
        # Note: 理论上没有任何入口可以删除内置管理账号，所以不可能为空
        user = DataSourceUser.objects.get(data_source=data_source)
        return Response(
            TenantBuiltinManagerRetrieveOutputSLZ(
                instance={
                    "username": user.username,
                    "enable_account_password_login": data_source.plugin_config["enable_account_password_login"],
                }
            ).data
        )

    @swagger_auto_schema(
        tags=["tenant_info"],
        operation_description="变更内置管理账号密码相关信息",
        request_body=TenantBuiltinManagerUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = TenantBuiltinManagerUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 查询租户的内置管理数据源
        data_source = DataSource.objects.get(
            owner_tenant_id=self.get_current_tenant_id(), type=DataSourceTypeEnum.BUILTIN_MANAGEMENT
        )
        # 数据源配置
        plugin_config = data_source.get_plugin_cfg()
        assert isinstance(plugin_config, LocalDataSourcePluginConfig)
        # 查询内置管理账号
        # Note: 理论上没有任何入口可以删除内置管理账号，所以不可能为空
        user = DataSourceUser.objects.get(data_source=data_source)

        # 更新
        with transaction.atomic():
            # 更新用户名
            if user.username != data["username"]:
                user.username = data["username"]
                user.updated_at = timezone.now()
                user.save(update_fields=["username", "updated_at"])
            # 更新是否启用登录
            if plugin_config.enable_account_password_login != data["enable_account_password_login"]:
                plugin_config.enable_account_password_login = data["enable_account_password_login"]
                data_source.set_plugin_cfg(plugin_config)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantBuiltinManagerPasswordUpdateApi(CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["tenant_info"],
        operation_description="重置内置管理账号密码",
        request_body=TenantBuiltinManagerPasswordUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        # 查询租户的内置管理数据源
        data_source = DataSource.objects.get(
            owner_tenant_id=self.get_current_tenant_id(), type=DataSourceTypeEnum.BUILTIN_MANAGEMENT
        )
        # 数据源配置
        plugin_config = data_source.get_plugin_cfg()
        assert isinstance(plugin_config, LocalDataSourcePluginConfig)
        assert plugin_config.password_rule is not None
        # 查询内置管理账号
        # Note: 理论上没有任何入口可以删除内置管理账号，所以不可能为空
        user = DataSourceUser.objects.get(data_source=data_source)

        slz = TenantBuiltinManagerPasswordUpdateInputSLZ(
            data=request.data,
            context={"plugin_config": plugin_config, "data_source_user_id": user.id},
        )
        slz.is_valid(raise_exception=True)
        raw_password = slz.validated_data["password"]

        DataSourceUserHandler.update_password(
            data_source_user=user,
            password=raw_password,
            valid_days=plugin_config.password_rule.valid_time,
            operator=request.user.username,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
