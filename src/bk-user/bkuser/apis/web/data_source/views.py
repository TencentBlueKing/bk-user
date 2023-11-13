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

import openpyxl
from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.data_source.mixins import CurrentUserTenantDataSourceMixin
from bkuser.apis.web.data_source.serializers import (
    DataSourceCreateInputSLZ,
    DataSourceCreateOutputSLZ,
    DataSourceImportOrSyncOutputSLZ,
    DataSourcePluginDefaultConfigOutputSLZ,
    DataSourcePluginOutputSLZ,
    DataSourceRandomPasswordInputSLZ,
    DataSourceRandomPasswordOutputSLZ,
    DataSourceRetrieveOutputSLZ,
    DataSourceSearchInputSLZ,
    DataSourceSearchOutputSLZ,
    DataSourceSwitchStatusOutputSLZ,
    DataSourceSyncRecordListOutputSLZ,
    DataSourceSyncRecordRetrieveOutputSLZ,
    DataSourceSyncRecordSearchInputSLZ,
    DataSourceTestConnectionInputSLZ,
    DataSourceTestConnectionOutputSLZ,
    DataSourceUpdateInputSLZ,
    LocalDataSourceImportInputSLZ,
)
from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.data_source.constants import DataSourceStatus
from bkuser.apps.data_source.models import DataSource, DataSourcePlugin, DataSourceSensitiveInfo
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.sync.constants import SyncTaskTrigger
from bkuser.apps.sync.data_models import DataSourceSyncOptions
from bkuser.apps.sync.managers import DataSourceSyncManager
from bkuser.apps.sync.models import DataSourceSyncTask
from bkuser.biz.data_source_plugin import DefaultPluginConfigProvider
from bkuser.biz.exporters import DataSourceUserExporter
from bkuser.common.error_codes import error_codes
from bkuser.common.passwd import PasswordGenerator
from bkuser.common.response import convert_workbook_to_response
from bkuser.common.views import ExcludePatchAPIViewMixin, ExcludePutAPIViewMixin
from bkuser.plugins.base import get_plugin_cfg_schema_map, get_plugin_cls
from bkuser.plugins.constants import DataSourcePluginEnum

logger = logging.getLogger(__name__)


class DataSourcePluginListApi(generics.ListAPIView):
    queryset = DataSourcePlugin.objects.all()
    pagination_class = None
    serializer_class = DataSourcePluginOutputSLZ

    @swagger_auto_schema(
        tags=["data_source_plugin"],
        operation_description="数据源插件列表",
        responses={status.HTTP_200_OK: DataSourcePluginOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DataSourcePluginDefaultConfigApi(generics.RetrieveAPIView):
    @swagger_auto_schema(
        tags=["data_source_plugin"],
        operation_description="数据源插件默认配置",
        responses={
            status.HTTP_200_OK: DataSourcePluginDefaultConfigOutputSLZ(),
            **get_plugin_cfg_schema_map(),
        },
    )
    def get(self, request, *args, **kwargs):
        config = DefaultPluginConfigProvider().get(kwargs["id"])
        if not config:
            raise error_codes.DATA_SOURCE_PLUGIN_NOT_DEFAULT_CONFIG

        return Response(DataSourcePluginDefaultConfigOutputSLZ(instance={"config": config.model_dump()}).data)


class DataSourceListCreateApi(CurrentUserTenantMixin, generics.ListCreateAPIView):
    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
    serializer_class = DataSourceSearchOutputSLZ

    def get_serializer_context(self):
        return {"data_source_plugin_map": dict(DataSourcePlugin.objects.values_list("id", "name"))}

    def get_queryset(self):
        slz = DataSourceSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        queryset = DataSource.objects.filter(owner_tenant_id=self.get_current_tenant_id())
        if kw := data.get("keyword"):
            queryset = queryset.filter(name__icontains=kw)

        return queryset

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源列表",
        query_serializer=DataSourceSearchInputSLZ(),
        responses={status.HTTP_200_OK: DataSourceSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="新建数据源",
        request_body=DataSourceCreateInputSLZ(),
        responses={
            status.HTTP_201_CREATED: DataSourceCreateOutputSLZ(),
            **get_plugin_cfg_schema_map(),
        },
    )
    def post(self, request, *args, **kwargs):
        current_tenant_id = self.get_current_tenant_id()
        slz = DataSourceCreateInputSLZ(data=request.data, context={"tenant_id": current_tenant_id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        with transaction.atomic():
            current_user = request.user.username
            ds = DataSource.objects.create(
                name=data["name"],
                owner_tenant_id=current_tenant_id,
                plugin=DataSourcePlugin.objects.get(id=data["plugin_id"]),
                plugin_config=data["plugin_config"],
                field_mapping=data["field_mapping"],
                sync_config=data.get("sync_config") or {},
                creator=current_user,
                updater=current_user,
            )

        return Response(
            DataSourceCreateOutputSLZ(instance={"id": ds.id}).data,
            status=status.HTTP_201_CREATED,
        )


class DataSourceRetrieveUpdateApi(
    CurrentUserTenantDataSourceMixin, ExcludePatchAPIViewMixin, generics.RetrieveUpdateAPIView
):
    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
    serializer_class = DataSourceRetrieveOutputSLZ

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源详情",
        responses={
            status.HTTP_200_OK: DataSourceRetrieveOutputSLZ(),
            **get_plugin_cfg_schema_map(),
        },
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="更新数据源",
        request_body=DataSourceUpdateInputSLZ(),
        responses={
            status.HTTP_204_NO_CONTENT: "",
            **get_plugin_cfg_schema_map(),
        },
    )
    def put(self, request, *args, **kwargs):
        data_source = self.get_object()
        slz = DataSourceUpdateInputSLZ(
            data=request.data,
            context={
                "plugin_id": data_source.plugin_id,
                "tenant_id": self.get_current_tenant_id(),
                "current_name": data_source.name,
                "exists_sensitive_infos": DataSourceSensitiveInfo.objects.filter(data_source=data_source),
            },
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        with transaction.atomic():
            data_source.name = data["name"]
            data_source.field_mapping = data["field_mapping"]
            data_source.sync_config = data.get("sync_config") or {}
            data_source.updater = request.user.username
            data_source.save(update_fields=["name", "field_mapping", "sync_config", "updater", "updated_at"])
            # 由于需要替换敏感信息，因此需要独立调用 set_plugin_cfg 方法
            data_source.set_plugin_cfg(data["plugin_config"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class DataSourceRandomPasswordApi(generics.CreateAPIView):
    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="生成数据源用户随机密码",
        request_body=DataSourceRandomPasswordInputSLZ(),
        responses={status.HTTP_200_OK: DataSourceRandomPasswordOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        slz = DataSourceRandomPasswordInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        passwd = PasswordGenerator(data["password_rule"]).generate()
        return Response(DataSourceRandomPasswordOutputSLZ(instance={"password": passwd}).data)


class DataSourceTestConnectionApi(CurrentUserTenantMixin, generics.CreateAPIView):
    """数据源连通性测试"""

    serializer_class = DataSourceTestConnectionOutputSLZ

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源连通性测试",
        request_body=DataSourceTestConnectionInputSLZ(),
        responses={status.HTTP_200_OK: DataSourceTestConnectionOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        slz = DataSourceTestConnectionInputSLZ(
            data=request.data,
            context={"tenant_id": self.get_current_tenant_id()},
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        plugin_id = data["plugin_id"]
        if plugin_id == DataSourcePluginEnum.LOCAL:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f("本地数据源插件不支持连通性测试")

        PluginCls = get_plugin_cls(plugin_id)  # noqa: N806
        result = PluginCls(data["plugin_config"]).test_connection()

        return Response(DataSourceTestConnectionOutputSLZ(instance=result).data)


class DataSourceSwitchStatusApi(CurrentUserTenantDataSourceMixin, ExcludePutAPIViewMixin, generics.UpdateAPIView):
    """切换数据源状态（启/停）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
    serializer_class = DataSourceSwitchStatusOutputSLZ

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="变更数据源状态",
        responses={status.HTTP_200_OK: DataSourceSwitchStatusOutputSLZ()},
    )
    def patch(self, request, *args, **kwargs):
        data_source = self.get_object()
        if data_source.status == DataSourceStatus.ENABLED:
            data_source.status = DataSourceStatus.DISABLED
        else:
            data_source.status = DataSourceStatus.ENABLED

        data_source.updater = request.user.username
        data_source.save(update_fields=["status", "updater", "updated_at"])

        return Response(DataSourceSwitchStatusOutputSLZ(instance={"status": data_source.status.value}).data)


class DataSourceTemplateApi(CurrentUserTenantDataSourceMixin, generics.ListAPIView):
    """获取本地数据源数据导入模板"""

    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="下载数据源导入模板",
        responses={status.HTTP_200_OK: "org_tmpl.xlsx"},
    )
    def get(self, request, *args, **kwargs):
        """数据源导出模板"""
        # 获取数据源信息，用于后续填充模板中的自定义字段
        data_source = self.get_object()
        if not data_source.is_local:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("仅本地数据源类型有提供导入模板"))

        workbook = DataSourceUserExporter(data_source).get_template()
        return convert_workbook_to_response(workbook, f"{settings.EXPORT_EXCEL_FILENAME_PREFIX}_org_tmpl.xlsx")


class DataSourceExportApi(CurrentUserTenantDataSourceMixin, generics.ListAPIView):
    """本地数据源用户导出"""

    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="下载本地数据源用户数据",
        responses={status.HTTP_200_OK: "org_data.xlsx"},
    )
    def get(self, request, *args, **kwargs):
        """导出指定的本地数据源用户数据（Excel 格式）"""
        data_source = self.get_object()
        if data_source.status != DataSourceStatus.ENABLED:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("数据源未启用"))

        if not data_source.is_local:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("仅能导出本地数据源数据"))

        workbook = DataSourceUserExporter(data_source).export()
        return convert_workbook_to_response(workbook, f"{settings.EXPORT_EXCEL_FILENAME_PREFIX}_org_data.xlsx")


class DataSourceImportApi(CurrentUserTenantDataSourceMixin, generics.CreateAPIView):
    """从 Excel 导入数据源用户数据"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="本地数据源用户数据导入",
        request_body=LocalDataSourceImportInputSLZ(),
        responses={status.HTTP_200_OK: DataSourceImportOrSyncOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        """从 Excel 导入数据源用户数据"""
        slz = LocalDataSourceImportInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source = self.get_object()
        if data_source.status != DataSourceStatus.ENABLED:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("数据源未启用"))

        if not data_source.is_local:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("仅本地数据源支持导入功能"))

        # Request file 转换成 openpyxl.workbook
        try:
            workbook = openpyxl.load_workbook(data["file"])
        except Exception:  # pylint: disable=broad-except
            logger.exception("本地数据源 %s 导入失败", data_source.id)
            raise error_codes.DATA_SOURCE_IMPORT_FAILED.f(_("文件格式异常"))

        options = DataSourceSyncOptions(
            operator=request.user.username,
            overwrite=data["overwrite"],
            incremental=data["incremental"],
            # FIXME (su) 本地数据源导入也要改成异步行为，但是要解决 excel 如何传递的问题
            async_run=False,
            trigger=SyncTaskTrigger.MANUAL,
        )

        try:
            plugin_init_extra_kwargs = {"workbook": workbook}
            task = DataSourceSyncManager(data_source, options).execute(plugin_init_extra_kwargs)
        except Exception as e:  # pylint: disable=broad-except
            # Q: 为什么不包装一层 DataSourceSyncError 而是捕获 Exception？
            # A: logger.exception 难以直接获取被包装的原始异常的抛出位置，影响问题定位，在找到优雅处理方法前，维持现状
            logger.exception("本地数据源 %s 导入失败", data_source.id)
            raise error_codes.DATA_SOURCE_IMPORT_FAILED.f(str(e))

        return Response(
            DataSourceImportOrSyncOutputSLZ(
                instance={"task_id": task.id, "status": task.status, "summary": task.summary}
            ).data
        )


class DataSourceSyncApi(CurrentUserTenantDataSourceMixin, generics.CreateAPIView):
    """数据源同步"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源数据同步",
        responses={status.HTTP_200_OK: DataSourceImportOrSyncOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        """触发数据源同步任务"""
        data_source = self.get_object()
        if data_source.status != DataSourceStatus.ENABLED:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("数据源未启用"))

        if data_source.is_local:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("本地数据源不支持同步，请使用导入功能"))

        # 同步策略：手动点击页面按钮，会触发全量覆盖的同步，且该同步是异步行为
        options = DataSourceSyncOptions(
            operator=request.user.username,
            overwrite=True,
            incremental=False,
            async_run=True,
            trigger=SyncTaskTrigger.MANUAL,
        )

        try:
            task = DataSourceSyncManager(data_source, options).execute()
        except Exception as e:  # pylint: disable=broad-except
            # Q: 为什么不包装一层 DataSourceSyncError 而是捕获 Exception？
            # A: logger.exception 难以直接获取被包装的原始异常的抛出位置，影响问题定位，在找到优雅处理方法前，维持现状
            logger.exception("创建下发数据源 %s 同步任务失败", data_source.id)
            raise error_codes.CREATE_DATA_SOURCE_SYNC_TASK_FAILED.f(str(e))

        return Response(
            DataSourceImportOrSyncOutputSLZ(
                instance={"task_id": task.id, "status": task.status, "summary": task.summary}
            ).data
        )


class DataSourceSyncRecordListApi(CurrentUserTenantMixin, generics.ListAPIView):
    """数据源同步记录列表"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
    serializer_class = DataSourceSyncRecordListOutputSLZ

    def get_queryset(self):
        slz = DataSourceSyncRecordSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        queryset = DataSourceSyncTask.objects.filter(data_source__owner_tenant_id=self.get_current_tenant_id())
        if data_source_id := data.get("data_source_id"):
            queryset = queryset.filter(data_source_id=data_source_id)

        if status := data.get("status"):
            queryset = queryset.filter(status=status)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["data_source_name_map"] = {
            ds.id: ds.name for ds in DataSource.objects.filter(owner_tenant_id=self.get_current_tenant_id())
        }
        return context

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源更新记录",
        query_serializer=DataSourceSyncRecordSearchInputSLZ(),
        responses={status.HTTP_200_OK: DataSourceSyncRecordListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DataSourceSyncRecordRetrieveApi(CurrentUserTenantMixin, generics.RetrieveAPIView):
    """数据源同步记录详情"""

    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    def get_queryset(self):
        return DataSourceSyncTask.objects.filter(data_source__owner_tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源更新日志",
        responses={status.HTTP_200_OK: DataSourceSyncRecordRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return Response(DataSourceSyncRecordRetrieveOutputSLZ(instance=self.get_object()).data)
