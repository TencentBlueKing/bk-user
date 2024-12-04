# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceSensitiveInfo
from bkuser.apps.idp.constants import INVALID_REAL_DATA_SOURCE_ID, IdpStatus
from bkuser.apps.idp.data_models import gen_data_source_match_rule_of_local
from bkuser.apps.idp.models import Idp, IdpPlugin, IdpSensitiveInfo
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.biz.auditor import DataSourceAuditor, IdpAuditor
from bkuser.common.error_codes import error_codes
from bkuser.common.views import ExcludePatchAPIViewMixin
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.idp_plugins.local.plugin import LocalIdpPluginConfig
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

from .schema import get_idp_plugin_cfg_json_schema, get_idp_plugin_cfg_openapi_schema_map
from .serializers import (
    IdpCreateInputSLZ,
    IdpCreateOutputSLZ,
    IdpListOutputSLZ,
    IdpPartialUpdateInputSLZ,
    IdpPluginConfigMetaRetrieveOutputSLZ,
    IdpPluginOutputSLZ,
    IdpRetrieveOutputSLZ,
    IdpSwitchStatusOutputSLZ,
    IdpUpdateInputSLZ,
    LocalIdpCreateInputSLZ,
    LocalIdpRetrieveOutputSLZ,
    LocalIdpUpdateInputSLZ,
)


class IdpPluginListApi(generics.ListAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

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


class IdpPluginConfigMetaRetrieveApi(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    queryset = IdpPlugin.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["idp_plugin"],
        operation_description="认证源插件默认配置",
        responses={status.HTTP_200_OK: IdpPluginConfigMetaRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        plugin = self.get_object()

        try:
            json_schema = get_idp_plugin_cfg_json_schema(plugin.id)
        except NotImplementedError:
            raise error_codes.IDP_PLUGIN_NOT_LOAD

        return Response(
            IdpPluginConfigMetaRetrieveOutputSLZ(instance={"id": plugin.id, "json_schema": json_schema}).data
        )


class IdpListCreateApi(CurrentUserTenantMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    pagination_class = None
    serializer_class = IdpListOutputSLZ

    def get_queryset(self):
        # 只查询实名数据源关联的认证源 或 实名数据源被删除后，关联的数据源 ID 被设置为无效的
        data_source = DataSource.objects.filter(
            owner_tenant_id=self.get_current_tenant_id(), type=DataSourceTypeEnum.REAL
        ).first()
        data_source_ids = (
            [data_source.id, INVALID_REAL_DATA_SOURCE_ID] if data_source is not None else [INVALID_REAL_DATA_SOURCE_ID]
        )

        return Idp.objects.filter(
            owner_tenant_id=self.get_current_tenant_id(), data_source_id__in=data_source_ids
        ).select_related("plugin")

    @swagger_auto_schema(
        tags=["idp"],
        operation_description="认证源列表",
        responses={status.HTTP_200_OK: IdpListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["idp"],
        operation_description="新建认证源",
        request_body=IdpCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: IdpCreateOutputSLZ(), **get_idp_plugin_cfg_openapi_schema_map()},
    )
    def post(self, request, *args, **kwargs):
        current_tenant_id = self.get_current_tenant_id()
        slz = IdpCreateInputSLZ(data=request.data, context={"tenant_id": current_tenant_id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        current_user = request.user.username
        plugin = IdpPlugin.objects.get(id=data["plugin_id"])

        idp = Idp.objects.create(
            name=data["name"],
            status=data["status"],
            owner_tenant_id=current_tenant_id,
            plugin=plugin,
            plugin_config=data["plugin_config"],
            data_source_match_rules=data["data_source_match_rules"],
            # Note: 当前页面只支持一个认证源配置一个数据源，所以直接取第一个即可
            data_source_id=data["data_source_match_rules"][0]["data_source_id"],
            creator=current_user,
            updater=current_user,
        )

        # 【审计】创建认证源审计对象
        auditor = IdpAuditor(request.user.username, current_tenant_id)
        # 【审计】将审计记录保存至数据库
        auditor.record_create(idp)

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
            **get_idp_plugin_cfg_openapi_schema_map(),
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
        responses={status.HTTP_204_NO_CONTENT: "", **get_idp_plugin_cfg_openapi_schema_map()},
    )
    def put(self, request, *args, **kwargs):
        idp = self.get_object()
        if idp.is_local:
            raise error_codes.CANNOT_UPDATE_IDP.f(_("该 API 不支持本地账密认证源更新配置"))

        current_tenant_id = self.get_current_tenant_id()
        slz = IdpUpdateInputSLZ(
            data=request.data,
            context={
                "tenant_id": current_tenant_id,
                "idp_id": idp.id,
                "plugin_id": idp.plugin_id,
                "exists_sensitive_infos": IdpSensitiveInfo.objects.filter(idp=idp),
            },
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 【审计】创建认证源审计对象，并记录变更前数据
        auditor = IdpAuditor(request.user.username, current_tenant_id)
        auditor.pre_record_data_before(idp)

        with transaction.atomic():
            idp.name = data["name"]
            idp.status = data["status"]
            idp.data_source_match_rules = data["data_source_match_rules"]
            idp.data_source_id = data["data_source_match_rules"][0]["data_source_id"]
            idp.updater = request.user.username
            idp.save(
                update_fields=["name", "status", "data_source_match_rules", "data_source_id", "updater", "updated_at"]
            )
            idp.set_plugin_cfg(data["plugin_config"])

        # 【审计】将审计记录保存至数据库
        auditor.record_update(idp)

        return Response(status=status.HTTP_204_NO_CONTENT)


class IdpStatusUpdateApi(CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    """切换认证源状态（启/停）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    serializer_class = IdpSwitchStatusOutputSLZ
    lookup_url_kwarg = "id"

    def get_queryset(self):
        # Note: 【防御性】当前产品页面未提供仅启停的功能
        #  1. 账密登录的启停涉及到密码功能启用，不能通过简单方式启停
        #  2. 无效数据源对应的认证源，需要经过修改后才可以启用
        return (
            Idp.objects.filter(owner_tenant_id=self.get_current_tenant_id())
            .exclude(plugin_id=BuiltinIdpPluginEnum.LOCAL)
            .exclude(data_source_id=INVALID_REAL_DATA_SOURCE_ID)
        )

    @swagger_auto_schema(
        tags=["idp"],
        operation_description="变更认证源状态",
        responses={status.HTTP_200_OK: IdpSwitchStatusOutputSLZ()},
    )
    def put(self, request, *args, **kwargs):
        idp = self.get_object()
        idp.status = IdpStatus.DISABLED if idp.status == IdpStatus.ENABLED else IdpStatus.ENABLED
        idp.updater = request.user.username
        idp.save(update_fields=["status", "updater", "updated_at"])

        return Response(IdpSwitchStatusOutputSLZ(instance={"status": idp.status.value}).data)


class LocalIdpCreateApi(CurrentUserTenantMixin, generics.CreateAPIView):
    """本地账密登录"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["idp"],
        operation_description="新建本地账密认证源",
        request_body=LocalIdpCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: IdpCreateOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        current_tenant_id = self.get_current_tenant_id()
        slz = LocalIdpCreateInputSLZ(data=request.data, context={"tenant_id": current_tenant_id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        current_user = request.user.username

        # 检测本地账密数据源是否存在
        data_source = DataSource.objects.filter(
            owner_tenant_id=current_tenant_id, type=DataSourceTypeEnum.REAL, plugin_id=DataSourcePluginEnum.LOCAL
        ).first()
        if data_source is None:
            raise error_codes.DATA_SOURCE_NOT_EXIST.f(_("数据源未配置或非本地类型数据源"))

        # 检查是否已经存在对应的认证源
        if Idp.objects.filter(
            owner_tenant_id=current_tenant_id, plugin_id=BuiltinIdpPluginEnum.LOCAL, data_source_id=data_source.id
        ).exists():
            raise error_codes.IDP_CREATE_FAILED.f(_("本地账密登录已存在"))

        plugin_config = data["plugin_config"]
        assert isinstance(plugin_config, LocalDataSourcePluginConfig)

        with transaction.atomic():
            idp = Idp.objects.create(
                name=data["name"],
                status=data["status"],
                owner_tenant_id=current_tenant_id,
                plugin_id=BuiltinIdpPluginEnum.LOCAL,
                plugin_config=LocalIdpPluginConfig(data_source_ids=[data_source.id]),
                data_source_match_rules=[gen_data_source_match_rule_of_local(data_source.id).model_dump()],
                data_source_id=data_source.id,
                creator=current_user,
                updater=current_user,
            )

            # 由于需要替换敏感信息，因此需要独立调用 set_plugin_cfg 方法
            data_source.set_plugin_cfg(plugin_config)

        # 【审计】创建认证源审计对象
        auditor = IdpAuditor(request.user.username, current_tenant_id)
        # 【审计】将审计记录保存至数据库
        auditor.record_create(idp)

        return Response(IdpCreateOutputSLZ(instance=idp).data, status=status.HTTP_201_CREATED)


class LocalIdpRetrieveUpdateApi(CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self):
        current_tenant_id = self.get_current_tenant_id()

        data_source = DataSource.objects.filter(
            owner_tenant_id=current_tenant_id, type=DataSourceTypeEnum.REAL, plugin_id=DataSourcePluginEnum.LOCAL
        ).first()
        if data_source is None:
            return Idp.objects.none()

        return Idp.objects.filter(
            owner_tenant_id=current_tenant_id, data_source_id=data_source.id, plugin_id=BuiltinIdpPluginEnum.LOCAL
        )

    @swagger_auto_schema(
        tags=["idp"],
        operation_description="本地认证源详情",
        responses={status.HTTP_200_OK: LocalIdpRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        idp = self.get_object()
        data_source = DataSource.objects.get(id=idp.data_source_id)

        return Response(
            LocalIdpRetrieveOutputSLZ(
                instance={
                    "id": idp.id,
                    "name": idp.name,
                    "status": idp.status,
                    "plugin_config": data_source.plugin_config,
                }
            ).data
        )

    @swagger_auto_schema(
        tags=["idp"],
        operation_description="更新本地认证源",
        request_body=LocalIdpUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        idp = self.get_object()
        data_source = DataSource.objects.get(id=idp.data_source_id)

        current_tenant_id = self.get_current_tenant_id()
        slz = LocalIdpUpdateInputSLZ(
            data=request.data,
            context={
                "tenant_id": current_tenant_id,
                "idp_id": idp.id,
                "exists_sensitive_infos": DataSourceSensitiveInfo.objects.filter(data_source=data_source),
            },
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 【审计】创建认证源审计对象并记录变更前数据
        idp_auditor = IdpAuditor(request.user.username, current_tenant_id)
        idp_auditor.pre_record_data_before(idp)
        # 【审计】创建数据源审计对象并记录变更前数据（本地数据源插件配置）
        ds_auditor = DataSourceAuditor(request.user.username, data_source.owner_tenant_id)
        ds_auditor.pre_record_data_before(data_source)

        with transaction.atomic():
            idp.name = data["name"]
            idp.status = data["status"]
            idp.updater = request.user.username
            idp.save(update_fields=["name", "status", "updater", "updated_at"])
            data_source.set_plugin_cfg(data["plugin_config"])

        # 【审计】将审计记录保存至数据库
        idp_auditor.record_update(idp)
        ds_auditor.record_update(data_source)

        return Response(status=status.HTTP_204_NO_CONTENT)
