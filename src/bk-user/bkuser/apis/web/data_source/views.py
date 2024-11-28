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

import logging

import openpyxl
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.data_source.mixins import CurrentUserTenantDataSourceMixin
from bkuser.apis.web.data_source.serializers import (
    DataSourceCreateInputSLZ,
    DataSourceCreateOutputSLZ,
    DataSourceDestroyInputSLZ,
    DataSourceImportOrSyncOutputSLZ,
    DataSourceListInputSLZ,
    DataSourceListOutputSLZ,
    DataSourcePluginConfigMetaRetrieveOutputSLZ,
    DataSourcePluginDefaultConfigOutputSLZ,
    DataSourcePluginOutputSLZ,
    DataSourceRandomPasswordInputSLZ,
    DataSourceRandomPasswordOutputSLZ,
    DataSourceRelatedResourceStatsOutputSLZ,
    DataSourceRetrieveOutputSLZ,
    DataSourceSyncRecordListOutputSLZ,
    DataSourceSyncRecordRetrieveOutputSLZ,
    DataSourceSyncRecordSearchInputSLZ,
    DataSourceTestConnectionInputSLZ,
    DataSourceTestConnectionOutputSLZ,
    DataSourceUpdateInputSLZ,
    LocalDataSourceImportInputSLZ,
)
from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourcePlugin,
    DataSourceSensitiveInfo,
    DataSourceUser,
)
from bkuser.apps.idp.constants import INVALID_REAL_DATA_SOURCE_ID, IdpStatus
from bkuser.apps.idp.models import Idp, IdpSensitiveInfo
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.sync.constants import SyncTaskTrigger
from bkuser.apps.sync.data_models import DataSourceSyncOptions
from bkuser.apps.sync.managers import DataSourceSyncManager
from bkuser.apps.sync.models import DataSourceSyncTask, TenantSyncTask
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.biz.auditor import DataSourceAuditor
from bkuser.biz.data_source import DataSourceHandler
from bkuser.biz.exporters import DataSourceUserExporter
from bkuser.biz.tenant import TenantUserHandler
from bkuser.common.error_codes import error_codes
from bkuser.common.passwd import PasswordGenerator
from bkuser.common.response import convert_workbook_to_response
from bkuser.common.views import ExcludePatchAPIViewMixin
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.plugins.base import get_default_plugin_cfg, get_plugin_cfg_schema_map, get_plugin_cls
from bkuser.plugins.constants import DataSourcePluginEnum

from .schema import get_data_source_plugin_cfg_json_schema

logger = logging.getLogger(__name__)


class DataSourcePluginListApi(generics.ListAPIView):
    """数据源插件列表"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

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
    """数据源插件默认配置"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    queryset = DataSourcePlugin.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["data_source_plugin"],
        operation_description="数据源插件默认配置",
        responses={
            status.HTTP_200_OK: DataSourcePluginDefaultConfigOutputSLZ(),
            **get_plugin_cfg_schema_map(),
        },
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            config = get_default_plugin_cfg(instance.id)
        except NotImplementedError:
            raise error_codes.DATA_SOURCE_PLUGIN_NOT_DEFAULT_CONFIG

        return Response(DataSourcePluginDefaultConfigOutputSLZ(instance={"config": config.model_dump()}).data)


class DataSourceListCreateApi(CurrentUserTenantMixin, generics.ListCreateAPIView):
    """数据源列表，创建"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    pagination_class = None
    serializer_class = DataSourceListOutputSLZ

    def get_queryset(self):
        slz = DataSourceListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        queryset = DataSource.objects.filter(owner_tenant_id=self.get_current_tenant_id())
        if type := data.get("type"):
            queryset = queryset.filter(type=type)

        return queryset

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源列表",
        query_serializer=DataSourceListInputSLZ(),
        responses={status.HTTP_200_OK: DataSourceListOutputSLZ(many=True)},
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
                owner_tenant_id=current_tenant_id,
                type=DataSourceTypeEnum.REAL,
                plugin=DataSourcePlugin.objects.get(id=data["plugin_id"]),
                plugin_config=data["plugin_config"],
                field_mapping=data["field_mapping"],
                sync_config=data.get("sync_config") or {},
                creator=current_user,
                updater=current_user,
            )

        # 【审计】创建数据源审计对象并记录
        auditor = DataSourceAuditor(request.user.username, current_tenant_id, ds)
        # 【审计】将审计记录保存至数据库
        auditor.record_create()

        return Response(
            DataSourceCreateOutputSLZ(instance={"id": ds.id}).data,
            status=status.HTTP_201_CREATED,
        )


class DataSourceRetrieveUpdateDestroyApi(
    CurrentUserTenantDataSourceMixin, ExcludePatchAPIViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    """数据源详情、更新、删除"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    pagination_class = None
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
        if not data_source.is_real_type:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("仅可更新实体类型数据源配置"))

        slz = DataSourceUpdateInputSLZ(
            data=request.data,
            context={
                "plugin_id": data_source.plugin_id,
                "tenant_id": self.get_current_tenant_id(),
                "exists_sensitive_infos": DataSourceSensitiveInfo.objects.filter(data_source=data_source),
            },
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 【审计】创建数据源审计对象，并记录变更前数据
        auditor = DataSourceAuditor(request.user.username, data_source.owner_tenant_id, data_source)
        auditor.pre_record_data_before()

        with transaction.atomic():
            data_source.field_mapping = data["field_mapping"]
            data_source.sync_config = data.get("sync_config") or {}
            data_source.updater = request.user.username
            data_source.save(update_fields=["field_mapping", "sync_config", "updater", "updated_at"])
            # 由于需要替换敏感信息，因此需要独立调用 set_plugin_cfg 方法
            data_source.set_plugin_cfg(data["plugin_config"])

        # 【审计】将审计记录保存至数据库
        auditor.record_update(data_source)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="重置数据源",
        query_serializer=DataSourceDestroyInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        """删除数据源及关联的其他数据"""
        data_source = self.get_object()
        if not data_source.is_real_type:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("仅可重置实体类型数据源"))

        slz = DataSourceDestroyInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        is_delete_idp = slz.validated_data["is_delete_idp"]

        idp_filters = {"owner_tenant_id": data_source.owner_tenant_id}

        if is_delete_idp:
            # 删除本地以及其他认证源，包括已禁用的认证源
            idp_filters["data_source_id__in"] = [INVALID_REAL_DATA_SOURCE_ID, data_source.id]
        else:
            # 仅删除本地认证源
            idp_filters["data_source_id"] = data_source.id
            idp_filters["plugin_id"] = BuiltinIdpPluginEnum.LOCAL

        # 待删除的认证源
        waiting_delete_idps = Idp.objects.filter(**idp_filters)

        # 【审计】创建数据源审计对象，并记录变更前数据
        auditor = DataSourceAuditor(request.user.username, data_source.owner_tenant_id, data_source)
        auditor.pre_record_data_before(list(waiting_delete_idps))

        with transaction.atomic():
            # 删除认证源敏感信息
            IdpSensitiveInfo.objects.filter(idp__in=waiting_delete_idps).delete()

            waiting_delete_idps.delete()

            if not is_delete_idp:
                # 禁用其他认证源
                Idp.objects.filter(owner_tenant_id=data_source.owner_tenant_id, data_source_id=data_source.id).update(
                    status=IdpStatus.DISABLED,
                    data_source_id=INVALID_REAL_DATA_SOURCE_ID,
                    updated_at=timezone.now(),
                    updater=request.user.username,
                )
            # 删除数据源 & 关联资源数据
            DataSourceHandler.delete_data_source_and_related_resources(data_source)

        # 【审计】将审计记录保存至数据库
        auditor.record_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class DataSourceRelatedResourceStatsApi(CurrentUserTenantDataSourceMixin, generics.RetrieveAPIView):
    """数据源关联资源信息"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"
    queryset = DataSource.objects.all()
    pagination_class = None
    serializer_class = DataSourceRelatedResourceStatsOutputSLZ

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源关联资源信息",
        responses={status.HTTP_200_OK: DataSourceRelatedResourceStatsOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        data_source = self.get_object()

        # 本租户自有的部门数量，即数据源部门数量，用户数量同理（会一比一同步成租户部门/用户）
        own_department_count = DataSourceDepartment.objects.filter(data_source=data_source).count()
        own_user_count = DataSourceUser.objects.filter(data_source=data_source).count()

        # 本租户分享给其他租户的：任意不属于本租户的租户部门/用户，但是数据源是本租户的
        shared_to_departments = TenantDepartment.objects.filter(
            data_source=data_source,
        ).exclude(tenant_id=data_source.owner_tenant_id)
        shared_to_users = TenantUser.objects.filter(
            data_source=data_source,
        ).exclude(tenant_id=data_source.owner_tenant_id)
        shared_to_tenant_count = len(
            set(shared_to_departments.values_list("tenant_id", flat=True))
            | set(shared_to_users.values_list("tenant_id", flat=True))
        )

        resources = {
            # own
            "own_department_count": own_department_count,
            "own_user_count": own_user_count,
            # shared to
            "shared_to_tenant_count": shared_to_tenant_count,
            "shared_to_department_count": shared_to_departments.count(),
            "shared_to_user_count": shared_to_users.count(),
        }
        return Response(DataSourceRelatedResourceStatsOutputSLZ(resources).data)


class DataSourceRandomPasswordApi(CurrentUserTenantMixin, generics.CreateAPIView):
    """生成数据源用户随机密码"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="生成数据源用户随机密码",
        request_body=DataSourceRandomPasswordInputSLZ(),
        responses={status.HTTP_200_OK: DataSourceRandomPasswordOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        slz = DataSourceRandomPasswordInputSLZ(
            data=request.data,
            context={"tenant_id": self.get_current_tenant_id()},
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        passwd = PasswordGenerator(data["password_rule"]).generate()
        return Response(DataSourceRandomPasswordOutputSLZ(instance={"password": passwd}).data)


class DataSourceTestConnectionApi(CurrentUserTenantMixin, generics.CreateAPIView):
    """数据源连通性测试"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

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
        result = PluginCls(data["plugin_config"], logger).test_connection()

        return Response(DataSourceTestConnectionOutputSLZ(instance=result).data)


class DataSourceTemplateApi(CurrentUserTenantDataSourceMixin, generics.ListAPIView):
    """获取本地数据源数据导入模板"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

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
        if not (data_source.is_local and data_source.is_real_type):
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("仅实体类型的本地数据源有提供导入模板"))

        workbook = DataSourceUserExporter(data_source).get_template()
        return convert_workbook_to_response(workbook, f"{settings.EXPORT_EXCEL_FILENAME_PREFIX}_org_tmpl.xlsx")


class DataSourceExportApi(CurrentUserTenantDataSourceMixin, generics.ListAPIView):
    """本地数据源用户导出"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    pagination_class = None

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="下载本地数据源用户数据",
        responses={status.HTTP_200_OK: "org_data.xlsx"},
    )
    def get(self, request, *args, **kwargs):
        """导出指定的本地数据源用户数据（Excel 格式）"""
        data_source = self.get_object()
        if not (data_source.is_local and data_source.is_real_type):
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("仅能导出实体类型的本地数据源数据"))

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
        if not (data_source.is_local and data_source.is_real_type):
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("仅实体类型的本地数据源支持导入功能"))

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
            async_run=True,
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

        # 【审计】创建数据源审计对象并记录
        auditor = DataSourceAuditor(request.user.username, data_source.owner_tenant_id, data_source)
        # 【审计】将审计记录保存至数据库
        auditor.record_sync(options)

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
        if data_source.is_local:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("本地数据源不支持同步，请使用导入功能"))

        if not data_source.is_real_type:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("仅实体类型的数据源支持同步"))

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
            raise error_codes.DATA_SOURCE_SYNC_TASK_CREATE_FAILED.f(str(e))

        # 【审计】创建数据源审计对象并记录
        auditor = DataSourceAuditor(request.user.username, data_source.owner_tenant_id, data_source)
        # 【审计】将审计记录保存至数据库
        auditor.record_sync(options)

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

        data_source = DataSource.objects.filter(
            owner_tenant_id=self.get_current_tenant_id(), id=self.kwargs["id"]
        ).first()
        if not data_source:
            raise error_codes.DATA_SOURCE_NOT_EXIST.f(_("数据源不存在"))

        if not data_source.is_real_type:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("仅实体类型的数据源有同步记录"))

        queryset = DataSourceSyncTask.objects.filter(data_source=data_source)
        if statuses := data.get("statuses"):
            queryset = queryset.filter(status__in=statuses)

        return queryset

    def get_serializer_context(self):
        cur_tenant_id = self.get_current_tenant_id()
        data_sources = DataSource.objects.filter(owner_tenant_id=cur_tenant_id)
        tenant_user_ids = DataSourceSyncTask.objects.filter(
            data_source__in=data_sources,
        ).values_list("operator", flat=True)
        tenant_sync_tasks = TenantSyncTask.objects.filter(data_source_owner_tenant_id=cur_tenant_id)
        return {
            "user_display_name_map": TenantUserHandler.get_tenant_user_display_name_map_by_ids(tenant_user_ids),
            "tenant_sync_task_map": {task.data_source_sync_task_id: task for task in tenant_sync_tasks},
        }

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

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self):
        return DataSourceSyncTask.objects.filter(data_source__owner_tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源更新日志",
        responses={status.HTTP_200_OK: DataSourceSyncRecordRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        data_source_sync_task = self.get_object()
        tenant_sync_task = TenantSyncTask.objects.filter(data_source_sync_task_id=data_source_sync_task.id).first()
        context = {"tenant_sync_task": tenant_sync_task}
        return Response(DataSourceSyncRecordRetrieveOutputSLZ(instance=data_source_sync_task, context=context).data)


class DataSourcePluginConfigMetaRetrieveApi(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    queryset = DataSourcePlugin.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["data_source"],
        operation_description="数据源插件配置元数据",
        responses={status.HTTP_200_OK: DataSourcePluginConfigMetaRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        plugin = self.get_object()

        try:
            json_schema = get_data_source_plugin_cfg_json_schema(plugin.id)
        except NotImplementedError:
            raise error_codes.DATA_SOURCE_PLUGIN_NOT_LOAD

        return Response(
            DataSourcePluginConfigMetaRetrieveOutputSLZ(instance={"id": plugin.id, "json_schema": json_schema}).data
        )
