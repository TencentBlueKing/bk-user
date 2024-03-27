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
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceDepartment, DataSourcePlugin, DataSourceUser
from bkuser.apps.data_source.utils import gen_tenant_user_id
from bkuser.apps.idp.models import Idp, IdpSensitiveInfo
from bkuser.apps.notification.tasks import send_reset_password_to_user
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.sync.tasks import initialize_identity_info_and_send_notification
from bkuser.apps.tenant.constants import DEFAULT_TENANT_USER_VALIDITY_PERIOD_CONFIG, TenantStatus
from bkuser.apps.tenant.models import (
    Tenant,
    TenantDepartment,
    TenantManager,
    TenantUser,
    TenantUserValidityPeriodConfig,
)
from bkuser.biz.data_source import DataSourceHandler
from bkuser.biz.data_source_organization import DataSourceUserHandler
from bkuser.common.error_codes import error_codes
from bkuser.common.views import ExcludePatchAPIViewMixin
from bkuser.plugins.base import get_default_plugin_cfg
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.constants import NotificationMethod, PasswordGenerateMethod
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

from .serializers import (
    TenantBuiltinManagerRetrieveOutputSLZ,
    TenantBuiltinManagerUpdateInputSLZ,
    TenantCreateInputSLZ,
    TenantCreateOutputSLZ,
    TenantListOutputSLZ,
    TenantRelatedResourceStatsOutputSLZ,
    TenantRetrieveOutputSLZ,
    TenantStatusUpdateOutputSLZ,
    TenantUpdateInputSLZ,
)


class TenantListCreateApi(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_PLATFORM)]

    pagination_class = None
    queryset = Tenant.objects.all()
    serializer_class = TenantListOutputSLZ

    @swagger_auto_schema(
        tags=["platform_management.tenant"],
        operation_description="租户列表",
        responses={status.HTTP_200_OK: TenantListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["platform_management.tenant"],
        operation_description="新建租户",
        request_body=TenantCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: TenantCreateOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        slz = TenantCreateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        with transaction.atomic():
            # 创建租户
            tenant = Tenant.objects.create(id=data["id"], name=data["name"], logo=data["logo"], status=data["status"])
            # 租户的一些默认配置初始化
            self._init_default_settings(tenant)

            # 创建内置管理的本地数据源
            data_source = self._create_builtin_management_data_source(
                tenant.id, data["fixed_password"], data["notification_method"]
            )

            # 添加内置管理账号
            self._add_builtin_management_user(
                tenant, data_source, data["email"], data["phone"], data["phone_country_code"]
            )

        # 对租户内置管理员进行账密信息初始化 & 发送密码通知
        # FIXME (nan): 调整：不需要经过账号初始化后发送密码，而是直接发送
        initialize_identity_info_and_send_notification.delay(data_source.id)

        return Response(TenantCreateOutputSLZ(instance={"id": tenant.id}).data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _init_default_settings(tenant: Tenant):
        """初始化租户的默认配置"""
        # 账号有效期
        TenantUserValidityPeriodConfig.objects.create(tenant=tenant, **DEFAULT_TENANT_USER_VALIDITY_PERIOD_CONFIG)

    @staticmethod
    def _create_builtin_management_data_source(
        tenant_id: str, fixed_password: str, notification_method: str
    ) -> DataSource:
        """创建租户内建管理的本地数据源"""
        # 获取本地数据源的默认配置
        plugin_id = DataSourcePluginEnum.LOCAL
        plugin_config = get_default_plugin_cfg(plugin_id)
        assert isinstance(plugin_config, LocalDataSourcePluginConfig)
        assert plugin_config.password_initial is not None

        # 修改为固定密码
        # FIXME (nan): 调整为直接发送账号密码后，不需要记录固定密码，直接使用默认配置的随机密码即可
        plugin_config.password_initial.generate_method = PasswordGenerateMethod.FIXED
        plugin_config.password_initial.fixed_password = fixed_password

        # 修改通知方式
        plugin_config.password_initial.notification.enabled_methods = [NotificationMethod(notification_method)]

        return DataSource.objects.create(
            type=DataSourceTypeEnum.BUILTIN_MANAGEMENT,
            owner_tenant_id=tenant_id,
            plugin=DataSourcePlugin.objects.get(id=plugin_id),
            plugin_config=plugin_config,
        )

    @staticmethod
    def _add_builtin_management_user(
        tenant: Tenant, data_source: DataSource, email: str, phone: str, phone_country_code: str
    ):
        """添加内置管理账号"""
        assert data_source.type == DataSourceTypeEnum.BUILTIN_MANAGEMENT

        username = f"admin-{tenant.id}"
        # 创建数据源用户
        data_source_user = DataSourceUser.objects.create(
            data_source=data_source,
            code=username,
            username=username,
            full_name=username,
            email=email,
            phone=phone,
            phone_country_code=phone_country_code,
        )

        # 创建对应的租户用户
        tenant_user = TenantUser.objects.create(
            id=gen_tenant_user_id(tenant.id, data_source, data_source_user),
            data_source_user=data_source_user,
            tenant=tenant,
            data_source=data_source,
        )

        # 添加为租户管理员
        TenantManager.objects.create(tenant=tenant, tenant_user=tenant_user)


class TenantRetrieveUpdateDestroyApi(ExcludePatchAPIViewMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_PLATFORM)]

    queryset = Tenant.objects.all()
    lookup_url_kwarg = "id"
    serializer_class = TenantRetrieveOutputSLZ

    @swagger_auto_schema(
        tags=["platform_management.tenant"],
        operation_description="租户详情",
        responses={status.HTTP_200_OK: TenantRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["platform_management.tenant"],
        operation_description="更新租户",
        request_body=TenantUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        tenant = self.get_object()
        slz = TenantUpdateInputSLZ(data=request.data, context={"tenant_id": tenant.id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 更新
        tenant.name = data["name"]
        tenant.logo = data["logo"]
        tenant.updater = request.user.username
        tenant.updated_at = timezone.now()
        tenant.save(update_fields=["name", "logo", "updater", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["platform_management.tenant"],
        operation_description="删除租户",
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        tenant = self.get_object()
        if tenant.is_default:
            raise error_codes.TENANT_DELETE_FAILED.f(_("默认租户不能删除"))

        if tenant.status != TenantStatus.DISABLED:
            raise error_codes.TENANT_DELETE_FAILED.f(_("需要先停用租户才能删除"))

        with transaction.atomic():
            # 删除租户配置的认证源
            idps = Idp.objects.filter(owner_tenant_id=tenant.id)
            IdpSensitiveInfo.objects.filter(idp__in=idps).delete()
            idps.delete()
            # 注：单租户数据源数量不多，且删除租户属于低频操作，可以走循环删除，暂不需要优化
            for data_source in DataSource.objects.filter(owner_tenant_id=tenant.id):
                DataSourceHandler.delete_data_source_and_related_resources(data_source)

            # 删除剩余的，通过协同创建的租户用户 / 部门（本租户数据源同步所得的，已经在删除数据源时候删除）
            # TODO (su) 协同相关数据的需要删除，比如协同策略，被协同的策略等等
            TenantUser.objects.filter(tenant=tenant).delete()
            TenantDepartment.objects.filter(tenant=tenant).delete()
            # 最后再删除租户
            tenant.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantStatusUpdateApi(ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    """切换租户状态（启/停）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_PLATFORM)]

    queryset = Tenant.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["platform_management.tenant"],
        operation_description="变更租户状态",
        responses={status.HTTP_200_OK: TenantStatusUpdateOutputSLZ()},
    )
    def put(self, request, *args, **kwargs):
        tenant = self.get_object()
        if tenant.is_default:
            raise error_codes.UPDATE_TENANT_FAILED.f(_("默认租户不能停用"))

        tenant.status = TenantStatus.DISABLED if tenant.status == TenantStatus.ENABLED else TenantStatus.ENABLED
        tenant.updater = request.user.username
        tenant.save(update_fields=["status", "updater", "updated_at"])

        return Response(TenantStatusUpdateOutputSLZ(instance={"status": tenant.status.value}).data)


class TenantBuiltinManagerRetrieveUpdateApi(ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    """内置租户管理账号"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_PLATFORM)]

    queryset = Tenant.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["platform_management.tenant"],
        operation_description="内置管理账号详情",
        responses={status.HTTP_200_OK: TenantBuiltinManagerRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant = self.get_object()
        # 查询租户的内置管理数据源
        data_source = DataSource.objects.get(owner_tenant_id=tenant.id, type=DataSourceTypeEnum.BUILTIN_MANAGEMENT)
        # 查询内置管理账号
        # Note: 理论上没有任何入口可以删除内置管理账号，所以不可能为空
        user = DataSourceUser.objects.get(data_source=data_source)

        return Response(TenantBuiltinManagerRetrieveOutputSLZ(instance={"username": user.username}).data)

    @swagger_auto_schema(
        tags=["platform_management.tenant"],
        operation_description="变更内置管理账号密码相关信息",
        request_body=TenantBuiltinManagerUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        tenant = self.get_object()
        # 查询内置管理数据源
        data_source = DataSource.objects.get(owner_tenant_id=tenant.id, type=DataSourceTypeEnum.BUILTIN_MANAGEMENT)
        # 数据源配置
        plugin_config = data_source.get_plugin_cfg()
        assert isinstance(plugin_config, LocalDataSourcePluginConfig)
        assert plugin_config.password_initial is not None
        assert plugin_config.password_rule is not None
        # 查询内置管理账号
        user = DataSourceUser.objects.get(data_source=data_source)

        slz = TenantBuiltinManagerUpdateInputSLZ(
            data=request.data,
            context={"plugin_config": plugin_config, "data_source_user_id": user.id},
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        fixed_password = data["fixed_password"]

        # 修改数据源配置
        # Note: plugin_config.password_initial.fixed_password 没必要修改，
        #  直接修改管理账号密码即可，第一次创建时为了发送, 修改时不需要调整了
        plugin_config.password_initial.notification.enabled_methods = [NotificationMethod(data["notification_method"])]

        # 更新
        with transaction.atomic():
            # 更新通知方式
            data_source.set_plugin_cfg(plugin_config)
            # 重置内置账号密码
            DataSourceUserHandler.update_password(
                data_source_user=user,
                password=fixed_password,
                valid_days=plugin_config.password_rule.valid_time,
                operator=request.user.username,
            )

        # 发送新密码通知到用户
        send_reset_password_to_user.delay(user.id, fixed_password)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantRelatedResourceStatsApi(generics.RetrieveAPIView):
    """获取租户关联资源信息"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_PLATFORM)]

    queryset = Tenant.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["platform_management.tenant"],
        operation_description="租户关联资源信息",
        responses={status.HTTP_200_OK: TenantRelatedResourceStatsOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant = self.get_object()
        data_sources = DataSource.objects.filter(owner_tenant_id=tenant.id)

        # TODO: 需要调整为虚拟账号数量、实名账号&部门数量、协同账号&部门数量（用户不关心数据源账号？）
        resources = {
            "data_source_count": data_sources.count(),
            "data_source_user_count": DataSourceUser.objects.filter(data_source__in=data_sources).count(),
            "data_source_department_count": DataSourceDepartment.objects.filter(data_source__in=data_sources).count(),
            # TODO (su) 支持协同后，可能关联到多个租户
            "tenant_count": 1,
            # 租户用户 / 部门数量 = 本租户数据源同步创建的（含分享给其他租户的） + 其他租户协同创建的（仅限于本租户）
            "tenant_user_count": TenantUser.objects.filter(
                Q(data_source__in=data_sources) | Q(tenant=tenant),
            ).count(),
            "tenant_department_count": TenantDepartment.objects.filter(
                Q(data_source__in=data_sources) | Q(tenant=tenant),
            ).count(),
        }
        return Response(TenantRelatedResourceStatsOutputSLZ(resources).data)
