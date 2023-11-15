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
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.idp.models import Idp, IdpPlugin
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.common.error_codes import error_codes
from bkuser.idp_plugins.base import get_plugin_cfg_schema_map

from .serializers import (
    IdpCreateInputSLZ,
    IdpCreateOutputSLZ,
    IdpPartialUpdateInputSLZ,
    IdpPluginOutputSLZ,
    IdpRetrieveOutputSLZ,
    IdpSearchInputSLZ,
    IdpSearchOutputSLZ,
    IdpUpdateInputSLZ,
)


class IdpPluginListApi(generics.ListAPIView):
    queryset = IdpPlugin.objects.all()
    pagination_class = None
    serializer_class = IdpPluginOutputSLZ

    @swagger_auto_schema(
        tags=["idp_plugin"],
        operation_description="认证源插件列表",
        responses={status.HTTP_200_OK: IdpPluginOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class IdpListCreateApi(CurrentUserTenantMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    pagination_class = None
    serializer_class = IdpSearchOutputSLZ

    def get_serializer_context(self):
        # TODO 目前未支持数据源跨租户协助，所以只查询本租户数据源
        data_source_name_map = dict(
            DataSource.objects.filter(owner_tenant_id=self.get_current_tenant_id()).values_list("id", "name")
        )
        return {"data_source_name_map": data_source_name_map}

    def get_queryset(self):
        slz = IdpSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        queryset = Idp.objects.filter(owner_tenant_id=self.get_current_tenant_id())
        if kw := data.get("keyword"):
            queryset = queryset.filter(name__icontains=kw)

        # 关联查询插件
        queryset.select_related("plugin")

        return queryset

    @swagger_auto_schema(
        tags=["idp"],
        operation_description="认证源列表",
        query_serializer=IdpSearchInputSLZ(),
        responses={status.HTTP_200_OK: IdpSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["idp"],
        operation_description="新建认证源",
        request_body=IdpCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: IdpCreateOutputSLZ(), **get_plugin_cfg_schema_map()},
    )
    def post(self, request, *args, **kwargs):
        current_tenant_id = self.get_current_tenant_id()
        slz = IdpCreateInputSLZ(data=request.data, context={"tenant_id": current_tenant_id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        current_user = request.user.username
        plugin = IdpPlugin.objects.get(id=data["plugin_id"])

        with transaction.atomic():
            idp = Idp.objects.create(
                name=data["name"],
                owner_tenant_id=current_tenant_id,
                plugin=plugin,
                plugin_config=data["plugin_config"],
                data_source_match_rules=data["data_source_match_rules"],
                creator=current_user,
                updater=current_user,
            )

        return Response(IdpCreateOutputSLZ(instance=idp).data, status=status.HTTP_201_CREATED)


class IdpRetrieveUpdateApi(CurrentUserTenantMixin, generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    serializer_class = IdpRetrieveOutputSLZ
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return Idp.objects.filter(owner_tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["idp"],
        operation_description="认证源详情",
        responses={
            status.HTTP_200_OK: IdpRetrieveOutputSLZ(),
            **get_plugin_cfg_schema_map(),
        },
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["idp"],
        operation_description="更新认证源部分字段",
        request_body=IdpPartialUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def patch(self, request, *args, **kwargs):
        idp = self.get_object()
        current_tenant_id = self.get_current_tenant_id()
        slz = IdpPartialUpdateInputSLZ(data=request.data, context={"tenant_id": current_tenant_id, "idp_id": idp.id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        idp.name = data["name"]
        idp.updater = request.user.username
        idp.save(update_fields=["name", "updater", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["idp"],
        operation_description="更新认证源",
        request_body=IdpUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: "", **get_plugin_cfg_schema_map()},
    )
    def put(self, request, *args, **kwargs):
        idp = self.get_object()
        if idp.is_local:
            raise error_codes.CANNOT_UPDATE_IDP.f(_("本地账密认证源不允许更新配置"))

        current_tenant_id = self.get_current_tenant_id()
        slz = IdpUpdateInputSLZ(
            data=request.data,
            context={"tenant_id": current_tenant_id, "idp_id": idp.id, "plugin_id": idp.plugin_id},
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        idp.name = data["name"]
        idp.plugin_config = data["plugin_config"]
        idp.data_source_match_rules = data["data_source_match_rules"]
        idp.updater = request.user.username
        idp.save(update_fields=["name", "plugin_config", "data_source_match_rules", "updater", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)
