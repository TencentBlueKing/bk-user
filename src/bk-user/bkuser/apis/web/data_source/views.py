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
from rest_framework.response import Response

from bkuser.apis.web.data_source.mixins import CurrentUserTenantDataSourceMixin
from bkuser.apis.web.data_source.serializers import (
    DataSourceCreateInputSLZ,
    DataSourceCreateOutputSLZ,
    DataSourcePluginDefaultConfigOutputSLZ,
    DataSourcePluginOutputSLZ,
    DataSourceRetrieveOutputSLZ,
    DataSourceSearchInputSLZ,
    DataSourceSearchOutputSLZ,
    DataSourceSwitchStatusOutputSLZ,
    DataSourceTestConnectionOutputSLZ,
    DataSourceUpdateInputSLZ,
    LocalDataSourceImportInputSLZ,
    LocalDataSourceImportOutputSLZ,
)
from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.data_source.constants import DataSourceStatus
from bkuser.apps.data_source.models import DataSource, DataSourcePlugin
from bkuser.apps.data_source.signals import post_create_data_source, post_update_data_source
from bkuser.apps.sync.constants import SyncTaskTrigger
from bkuser.apps.sync.data_models import DataSourceSyncOptions
from bkuser.apps.sync.managers import DataSourceSyncManager
from bkuser.biz.data_source_plugin import DefaultPluginConfigProvider
from bkuser.biz.exporters import DataSourceUserExporter
from bkuser.common.error_codes import error_codes
from bkuser.common.response import convert_workbook_to_response
from bkuser.common.views import ExcludePatchAPIViewMixin, ExcludePutAPIViewMixin
from bkuser.plugins.constants import DATA_SOURCE_PLUGIN_CONFIG_SCHEMA_MAP

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
            **DATA_SOURCE_PLUGIN_CONFIG_SCHEMA_MAP,
        },
    )
    def get(self, request, *args, **kwargs):
        config = DefaultPluginConfigProvider().get(kwargs["id"])
        if not config:
            raise error_codes.DATA_SOURCE_PLUGIN_NOT_DEFAULT_CONFIG

        return Response(DataSourcePluginDefaultConfigOutputSLZ(instance={"config": config.model_dump()}).data)


class DataSourceListCreateApi(CurrentUserTenantMixin, generics.ListCreateAPIView):
    pagination_class = None
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
            **DATA_SOURCE_PLUGIN_CONFIG_SCHEMA_MAP,
        },
    )
    def post(self, request, *args, **kwargs):
        slz = DataSourceCreateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        with transaction.atomic():
            current_user = request.user.username
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
            DataSourceCreateOutputSLZ(instance={"id": ds.id}).data,
            status=status.HTTP_201_CREATED,
        )


class DataSourceRetrieveUpdateApi(
    CurrentUserTenantDataSourceMixin, ExcludePatchAPIViewMixin, generics.RetrieveUpdateAPIView
):
    pagination_class = None
    serializer_class = DataSourceRetrieveOutputSLZ

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源详情",
        responses={
            status.HTTP_200_OK: DataSourceRetrieveOutputSLZ(),
            **DATA_SOURCE_PLUGIN_CONFIG_SCHEMA_MAP,
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
            **DATA_SOURCE_PLUGIN_CONFIG_SCHEMA_MAP,
        },
    )
    def put(self, request, *args, **kwargs):
        data_source = self.get_object()
        slz = DataSourceUpdateInputSLZ(
            data=request.data,
            context={"plugin_id": data_source.plugin_id},
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        with transaction.atomic():
            data_source.plugin_config = data["plugin_config"]
            data_source.field_mapping = data["field_mapping"]
            data_source.updater = request.user.username
            data_source.save()

            post_update_data_source.send(sender=self.__class__, data_source=data_source)

        return Response(status=status.HTTP_204_NO_CONTENT)


class DataSourceTestConnectionApi(CurrentUserTenantDataSourceMixin, generics.RetrieveAPIView):
    """数据源连通性测试"""

    serializer_class = DataSourceTestConnectionOutputSLZ

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源连通性测试",
        responses={status.HTTP_200_OK: DataSourceTestConnectionOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        data_source = self.get_object()
        if data_source.is_local:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED

        # TODO (su) 实现代码逻辑，需调用数据源插件以确认连通性
        mock_data = {
            "error_message": "",
            "user": {
                "id": "uid_2",
                "properties": {
                    "username": "zhangSan",
                },
                "leaders": ["uid_0", "uid_1"],
                "departments": ["dept_id_1"],
            },
            "department": {
                "id": "dept_id_1",
                "name": "dept_name",
                "parent": "dept_id_0",
            },
        }

        return Response(DataSourceTestConnectionOutputSLZ(instance=mock_data).data)


class DataSourceSwitchStatusApi(CurrentUserTenantDataSourceMixin, ExcludePutAPIViewMixin, generics.UpdateAPIView):
    """切换数据源状态（启/停）"""

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

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="下载本地数据源用户数据",
        responses={status.HTTP_200_OK: "org_data.xlsx"},
    )
    def get(self, request, *args, **kwargs):
        """导出指定的本地数据源用户数据（Excel 格式）"""
        data_source = self.get_object()
        if not data_source.is_local:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("仅能导出本地数据源数据"))

        workbook = DataSourceUserExporter(data_source).export()
        return convert_workbook_to_response(workbook, f"{settings.EXPORT_EXCEL_FILENAME_PREFIX}_org_data.xlsx")


class DataSourceImportApi(CurrentUserTenantDataSourceMixin, generics.CreateAPIView):
    """从 Excel 导入数据源用户数据"""

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="本地数据源用户数据导入",
        request_body=LocalDataSourceImportInputSLZ(),
        responses={status.HTTP_200_OK: LocalDataSourceImportOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        """从 Excel 导入数据源用户数据"""
        slz = LocalDataSourceImportInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source = self.get_object()
        if not data_source.is_local:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("仅本地数据源支持导入功能"))

        # Request file 转换成 openpyxl.workbook
        try:
            workbook = openpyxl.load_workbook(data["file"])
        except Exception:  # pylint: disable=broad-except
            logger.exception("本地数据源导入失败")
            raise error_codes.DATA_SOURCE_IMPORT_FAILED.f(_("文件格式异常"))

        options = DataSourceSyncOptions(
            operator=request.user.username,
            overwrite=data["overwrite"],
            incremental=data["incremental"],
            async_run=False,
            trigger=SyncTaskTrigger.MANUAL,
        )

        try:
            plugin_init_extra_kwargs = {"workbook": workbook}
            task = DataSourceSyncManager(data_source, options).execute(plugin_init_extra_kwargs)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("本地数据源导入失败")
            raise error_codes.DATA_SOURCE_IMPORT_FAILED.f(str(e))

        return Response(
            LocalDataSourceImportOutputSLZ(
                instance={"task_id": task.id, "status": task.status, "summary": task.summary}
            ).data
        )


class DataSourceSyncApi(generics.CreateAPIView):
    """数据源同步"""

    def post(self, request, *args, **kwargs):
        """触发数据源同步任务"""
        # TODO (su) 实现代码逻辑，注意：本地数据源应该使用导入，而不是同步
        return Response()
