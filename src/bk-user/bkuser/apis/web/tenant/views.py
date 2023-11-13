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

from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.tenant.serializers import (
    TenantCreateInputSLZ,
    TenantCreateOutputSLZ,
    TenantRetrieveOutputSLZ,
    TenantSearchInputSLZ,
    TenantSearchOutputSLZ,
    TenantUpdateInputSLZ,
    TenantUserSearchInputSLZ,
    TenantUserSearchOutputSLZ,
)
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.models import Tenant, TenantUser
from bkuser.biz.data_source import DataSourceHandler
from bkuser.biz.tenant import (
    TenantBaseInfo,
    TenantEditableBaseInfo,
    TenantFeatureFlag,
    TenantHandler,
    TenantManagerWithoutID,
)
from bkuser.common.views import ExcludePatchAPIViewMixin
from bkuser.plugins.local.models import PasswordInitialConfig

logger = logging.getLogger(__name__)


class TenantListCreateApi(generics.ListCreateAPIView):
    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_PLATFORM)]
    serializer_class = TenantSearchOutputSLZ

    def get_serializer_context(self):
        # set into context, for slz to_representation
        return {
            "tenant_manager_map": TenantHandler.get_tenant_manager_map(),
            "data_source_map": DataSourceHandler.get_data_source_map_by_owner(),
        }

    def get_queryset(self):
        slz = TenantSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        queryset = Tenant.objects.all()

        if data.get("name"):
            queryset = Tenant.objects.filter(name__icontains=data["name"])

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
        tenant_info = TenantBaseInfo(id=data["id"], name=data["name"], feature_flags=feature_flags, logo=data["logo"])
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

        return Response(TenantCreateOutputSLZ(instance={"id": tenant_id}).data)


class TenantRetrieveUpdateApi(ExcludePatchAPIViewMixin, generics.RetrieveUpdateAPIView):
    queryset = Tenant.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_PLATFORM)]
    serializer_class = TenantRetrieveOutputSLZ

    def get_serializer_context(self):
        # set into context, for slz to_representation
        tenant_id = self.kwargs[self.lookup_url_kwarg]
        return {
            "tenant_manager_map": TenantHandler.get_tenant_manager_map(tenant_ids=[tenant_id]),
        }

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
        responses={status.HTTP_200_OK: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = TenantUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        instance = self.get_object()

        should_updated_info = TenantEditableBaseInfo(
            name=data["name"], logo=data.get("logo") or "", feature_flags=TenantFeatureFlag(**data["feature_flags"])
        )

        TenantHandler.update_with_managers(instance.id, should_updated_info, data["manager_ids"])

        return Response()


class TenantUsersListApi(generics.ListAPIView):
    serializer_class = TenantUserSearchOutputSLZ
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_PLATFORM)]

    def get_queryset(self):
        tenant_id = self.kwargs["tenant_id"]
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
