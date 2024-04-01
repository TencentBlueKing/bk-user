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
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import LocalDataSourceIdentityInfo
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.models import Tenant, TenantManager, TenantUser
from bkuser.biz.data_source_organization import DataSourceUserHandler
from bkuser.common.views import ExcludePatchAPIViewMixin, ExcludePutAPIViewMixin
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

from .mixins import CurrentTenantBuiltinDataSourceUserMixin
from .serializers import (
    TenantBuiltinManagerPasswordUpdateInputSLZ,
    TenantBuiltinManagerRetrieveOutputSLZ,
    TenantBuiltinManagerUpdateInputSLZ,
    TenantRealManagerCreateInputSLZ,
    TenantRealManagerDestroyInputSLZ,
    TenantRealManagerListOutputSLZ,
    TenantRealUserListInputSLZ,
    TenantRealUserListOutputSLZ,
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
        tenant.save(update_fields=["name", "logo", "visible", "user_number_visible", "updater", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantBuiltinManagerRetrieveUpdateApi(
    CurrentTenantBuiltinDataSourceUserMixin, ExcludePutAPIViewMixin, generics.RetrieveUpdateAPIView
):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["tenant_info"],
        operation_description="租户内置管理账号信息",
        responses={status.HTTP_200_OK: TenantBuiltinManagerRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        data_source, user = self.get_builtin_data_source_and_user()
        return Response(
            TenantBuiltinManagerRetrieveOutputSLZ(
                {
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
    def patch(self, request, *args, **kwargs):
        slz = TenantBuiltinManagerUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 内建数据源 & 用户
        data_source, user = self.get_builtin_data_source_and_user()

        # 数据源配置
        plugin_config = data_source.get_plugin_cfg()
        assert isinstance(plugin_config, LocalDataSourcePluginConfig)

        # 更新
        with transaction.atomic():
            # 更新用户名
            new_username = data.get("username")
            if new_username and user.username != new_username:
                user.username = new_username
                user.save(update_fields=["username", "updated_at"])
                # Note: 必须同步修改账密信息里的用户名
                LocalDataSourceIdentityInfo.objects.filter(user=user).update(username=new_username)

            # 更新是否启用登录
            enable = data.get("enable_account_password_login")
            if enable is not None and plugin_config.enable_account_password_login != enable:
                plugin_config.enable_account_password_login = enable
                data_source.set_plugin_cfg(plugin_config)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantBuiltinManagerPasswordUpdateApi(
    CurrentTenantBuiltinDataSourceUserMixin, ExcludePatchAPIViewMixin, generics.UpdateAPIView
):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["tenant_info"],
        operation_description="重置内置管理账号密码",
        request_body=TenantBuiltinManagerPasswordUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        # 内建数据源 & 用户
        data_source, user = self.get_builtin_data_source_and_user()

        # 数据源配置
        plugin_config = data_source.get_plugin_cfg()
        assert isinstance(plugin_config, LocalDataSourcePluginConfig)
        assert plugin_config.password_rule is not None

        # 数据校验
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


class TenantRealManagerListCreateDestroyApi(
    CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.ListCreateAPIView, generics.DestroyAPIView
):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    pagination_class = None
    serializer_class = TenantRealManagerListOutputSLZ

    def get_queryset(self):
        return TenantManager.objects.filter(
            tenant_id=self.get_current_tenant_id(), tenant_user__data_source__type=DataSourceTypeEnum.REAL
        ).select_related("tenant_user__data_source_user")

    @swagger_auto_schema(
        tags=["tenant_info"],
        operation_description="租户实名管理员列表",
        responses={status.HTTP_200_OK: TenantRealManagerListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["tenant_info"],
        operation_description="批量添加租户实名管理员",
        request_body=TenantRealManagerCreateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def post(self, request, *args, **kwargs):
        tenant_id = self.get_current_tenant_id()
        slz = TenantRealManagerCreateInputSLZ(data=request.data, context={"tenant_id": tenant_id})
        slz.is_valid(raise_exception=True)
        ids = slz.validated_data["ids"]

        # 查询租户已有的所有实名管理账号，用于去重，避免后续创建重复
        old_ids = list(
            TenantManager.objects.filter(
                tenant_id=tenant_id, tenant_user__data_source__type=DataSourceTypeEnum.REAL
            ).values_list("tenant_user_id", flat=True)
        )

        if waiting_create_ids := set(ids) - set(old_ids):
            TenantManager.objects.bulk_create(
                [TenantManager(tenant_id=tenant_id, tenant_user_id=i) for i in waiting_create_ids]
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["tenant_info"],
        operation_description="批量移除租户实名管理员",
        query_serializer=TenantRealManagerDestroyInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def destroy(self, request, *args, **kwargs):
        slz = TenantRealManagerDestroyInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        ids = slz.validated_data["ids"]

        if ids:
            TenantManager.objects.filter(
                tenant_id=self.get_current_tenant_id(),
                tenant_user__data_source__type=DataSourceTypeEnum.REAL,
                tenant_user_id__in=ids,
            ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantRealUserListApi(CurrentUserTenantMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    serializer_class = TenantRealUserListOutputSLZ

    def get_queryset(self):
        slz = TenantRealUserListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        tenant_id = self.get_current_tenant_id()

        # 只过滤本租户且为实名的用户
        queryset = TenantUser.objects.filter(
            tenant_id=tenant_id, data_source__type=DataSourceTypeEnum.REAL
        ).select_related("data_source_user")

        # 排除已经是管理员的实名用户
        if data.get("exclude_manager"):
            manager_ids = list(
                TenantManager.objects.filter(
                    tenant_id=tenant_id, tenant_user__data_source__type=DataSourceTypeEnum.REAL
                ).values_list("tenant_user_id", flat=True)
            )
            queryset = queryset.exclude(id__in=manager_ids)

        # 关键字过滤
        if keyword := data.get("keyword"):
            queryset = queryset.filter(
                Q(data_source_user__username__icontains=keyword) | Q(data_source_user__full_name__icontains=keyword)
            )

        return queryset

    @swagger_auto_schema(
        tags=["tenant_info"],
        operation_description="租户实名用户列表",
        query_serializer=TenantRealUserListInputSLZ(),
        responses={status.HTTP_200_OK: TenantRealUserListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
