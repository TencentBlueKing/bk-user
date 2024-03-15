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
import logging
from collections import defaultdict

from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.tenant.serializers import (
    TenantCreateInputSLZ,
    TenantCreateOutputSLZ,
    TenantRelatedResourcesListOutputSLZ,
    TenantRetrieveOutputSLZ,
    TenantSearchInputSLZ,
    TenantSearchOutputSLZ,
    TenantSwitchStatusOutputSLZ,
    TenantUpdateInputSLZ,
    TenantUserSearchInputSLZ,
    TenantUserSearchOutputSLZ,
)
from bkuser.apps.data_source.models import DataSource, DataSourceDepartment, DataSourceUser
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.constants import TenantStatus
from bkuser.apps.tenant.models import Tenant, TenantDepartment, TenantManager, TenantUser
from bkuser.biz.data_source import DataSourceHandler
from bkuser.biz.tenant import (
    TenantEditableInfo,
    TenantFeatureFlag,
    TenantHandler,
    TenantInfo,
    TenantManagerWithoutID,
)
from bkuser.common.error_codes import error_codes
from bkuser.common.views import ExcludePatchAPIViewMixin, ExcludePutAPIViewMixin
from bkuser.plugins.local.models import PasswordInitialConfig

logger = logging.getLogger(__name__)


class TenantListCreateApi(generics.ListCreateAPIView):
    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_PLATFORM)]
    serializer_class = TenantSearchOutputSLZ

    def get_serializer_context(self):
        # {租户：租户管理员信息}
        tenant_manager_map = defaultdict(list)
        for m in TenantManager.objects.select_related("tenant_user__data_source_user"):
            tenant_manager_map[m.tenant_id].append(
                {
                    "id": m.tenant_user.id,
                    "username": m.tenant_user.data_source_user.username,
                    "full_name": m.tenant_user.data_source_user.full_name,
                }
            )
        # {租户：数据源信息}
        tenant_data_source_map = defaultdict(list)
        for ds in DataSource.objects.all():
            tenant_data_source_map[ds.owner_tenant_id].append({"id": ds.id, "name": ds.name})

        return {
            "tenant_manager_map": tenant_manager_map,
            "tenant_data_source_map": tenant_data_source_map,
        }

    def get_queryset(self):
        slz = TenantSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        queryset = Tenant.objects.all()
        if data.get("name"):
            queryset = queryset.filter(name__icontains=data["name"])

        return queryset

    @swagger_auto_schema(
        tags=["tenant"],
        operation_description="租户列表",
        query_serializer=TenantSearchInputSLZ(),
        responses={status.HTTP_200_OK: TenantSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["tenant"],
        operation_description="新建租户",
        request_body=TenantCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: TenantCreateOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        slz = TenantCreateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 初始化租户和租户管理员
        feature_flags = TenantFeatureFlag(**data["feature_flags"])
        tenant_info = TenantInfo(
            id=data["id"],
            name=data["name"],
            feature_flags=feature_flags,
            logo=data["logo"],
        )
        managers = [
            TenantManagerWithoutID(
                username=i["username"],
                full_name=i["full_name"],
                email=i["email"],
                phone=i["phone"],
                phone_country_code=i["phone_country_code"],
            )
            for i in data["managers"]
        ]
        # 本地数据源密码初始化配置
        config = PasswordInitialConfig(**data["password_initial_config"])

        # 创建租户和租户管理员
        tenant_id = TenantHandler.create_with_managers(tenant_info, managers, config)

        return Response(TenantCreateOutputSLZ(instance={"id": tenant_id}).data, status=status.HTTP_201_CREATED)


class TenantRetrieveUpdateDestroyApi(ExcludePatchAPIViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Tenant.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_PLATFORM)]
    serializer_class = TenantRetrieveOutputSLZ

    @swagger_auto_schema(
        tags=["tenant"],
        operation_description="租户详情",
        responses={status.HTTP_200_OK: TenantRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["tenant"],
        operation_description="更新租户",
        request_body=TenantUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = TenantUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant_info = TenantEditableInfo(
            name=data["name"],
            logo=data.get("logo") or "",
            feature_flags=TenantFeatureFlag(**data["feature_flags"]),
        )

        TenantHandler.update_with_managers(self.get_object().id, tenant_info, data["manager_ids"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["tenant"],
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


class TenantRelatedResourceStatsApi(generics.RetrieveAPIView):
    """获取租户关联资源信息"""

    queryset = Tenant.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_PLATFORM)]
    serializer_class = TenantRelatedResourcesListOutputSLZ

    @swagger_auto_schema(
        tags=["tenant"],
        operation_description="租户关联资源信息",
        responses={status.HTTP_200_OK: TenantRelatedResourcesListOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant = self.get_object()
        data_sources = DataSource.objects.filter(owner_tenant_id=tenant.id)

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
        return Response(TenantRelatedResourcesListOutputSLZ(resources).data)


class TenantSwitchStatusApi(ExcludePutAPIViewMixin, generics.UpdateAPIView):
    """切换租户状态（启/停）"""

    queryset = Tenant.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_PLATFORM)]
    serializer_class = TenantSwitchStatusOutputSLZ

    @swagger_auto_schema(
        tags=["tenant"],
        operation_description="变更租户状态",
        responses={status.HTTP_200_OK: TenantSwitchStatusOutputSLZ()},
    )
    def patch(self, request, *args, **kwargs):
        tenant = self.get_object()
        if tenant.is_default:
            raise error_codes.UPDATE_TENANT_FAILED.f(_("默认租户不能停用"))

        tenant.status = TenantStatus.DISABLED if tenant.status == TenantStatus.ENABLED else TenantStatus.ENABLED
        tenant.updater = request.user.username
        tenant.save(update_fields=["status", "updater", "updated_at"])

        return Response(TenantSwitchStatusOutputSLZ(instance={"status": tenant.status.value}).data)


class TenantUsersListApi(generics.ListAPIView):
    serializer_class = TenantUserSearchOutputSLZ
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_PLATFORM)]

    def get_queryset(self):
        tenant_id = self.kwargs["id"]
        slz = TenantUserSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        queryset = TenantUser.objects.select_related("data_source_user").filter(tenant_id=tenant_id)
        if keyword := data.get("keyword"):
            queryset = queryset.filter(
                Q(data_source_user__username__icontains=keyword) | Q(data_source_user__full_name__icontains=keyword)
            )

        return queryset

    @swagger_auto_schema(
        tags=["tenant"],
        operation_description="租户下用户列表",
        query_serializer=TenantUserSearchInputSLZ(),
        responses={status.HTTP_200_OK: TenantUserSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
