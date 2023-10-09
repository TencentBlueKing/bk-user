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
from typing import Any, Dict, List

from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_serializer_method
from pydantic import ValidationError as PDValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import FieldMappingOperation
from bkuser.apps.data_source.models import DataSource, DataSourcePlugin
from bkuser.apps.tenant.models import TenantUserCustomField, UserBuiltinField
from bkuser.plugins.base import get_plugin_cfg_cls
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.models import DataSourceSyncConfig
from bkuser.utils.pydantic import stringify_pydantic_error

logger = logging.getLogger(__name__)


class DataSourceSearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", required=False)


class DataSourceSearchOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="数据源 ID")
    name = serializers.CharField(help_text="数据源名称")
    owner_tenant_id = serializers.CharField(help_text="数据源所属租户 ID")
    plugin_id = serializers.CharField(help_text="数据源插件 ID")
    plugin_name = serializers.SerializerMethodField(help_text="数据源插件名称")
    cooperation_tenants = serializers.SerializerMethodField(help_text="协作公司")
    status = serializers.CharField(help_text="数据源状态")
    updater = serializers.CharField(help_text="更新者")
    updated_at = serializers.SerializerMethodField(help_text="更新时间")

    def get_plugin_name(self, obj: DataSource) -> str:
        return self.context["data_source_plugin_map"].get(obj.plugin_id, "")

    @swagger_serializer_method(
        serializer_or_field=serializers.ListField(
            help_text="协作公司",
            child=serializers.CharField(),
            allow_empty=True,
        )
    )
    def get_cooperation_tenants(self, obj: DataSource) -> List[str]:
        # TODO 目前未支持数据源跨租户协作，因此该数据均为空
        return []

    def get_updated_at(self, obj: DataSource) -> str:
        return obj.updated_at_display


class DataSourceFieldMappingSLZ(serializers.Serializer):
    """单个数据源字段映射"""

    source_field = serializers.CharField(help_text="数据源原始字段")
    mapping_operation = serializers.ChoiceField(help_text="映射关系", choices=FieldMappingOperation.get_choices())
    target_field = serializers.CharField(help_text="目标字段")
    expression = serializers.CharField(help_text="表达式", required=False)


class DataSourceCreateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="数据源名称", max_length=128)
    plugin_id = serializers.CharField(help_text="数据源插件 ID")
    plugin_config = serializers.JSONField(help_text="数据源插件配置")
    field_mapping = serializers.ListField(
        help_text="用户字段映射", child=DataSourceFieldMappingSLZ(), allow_empty=True, required=False, default=list
    )
    sync_config = serializers.JSONField(help_text="数据源同步配置", default=dict)

    def validate_name(self, name: str) -> str:
        if DataSource.objects.filter(name=name).exists():
            raise ValidationError(_("同名数据源已存在"))

        return name

    def validate_plugin_id(self, plugin_id: str) -> str:
        if not DataSourcePlugin.objects.filter(id=plugin_id).exists():
            raise ValidationError(_("数据源插件不存在"))

        return plugin_id

    def validate_field_mapping(self, field_mapping: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        target_fields = {m.get("target_field") for m in field_mapping}
        allowed_target_fields = list(UserBuiltinField.objects.all().values_list("name", flat=True)) + list(
            TenantUserCustomField.objects.filter(tenant_id=self.context["tenant_id"]).values_list("name", flat=True)
        )
        if not_allowed_fields := target_fields - set(allowed_target_fields):
            raise ValidationError(
                _("字段映射中的目标字段 {} 不属于用户自定义字段或内置字段").format(not_allowed_fields),
            )

        return field_mapping

    def validate_sync_config(self, sync_config: Dict[str, Any]) -> Dict[str, Any]:
        if not sync_config:
            return sync_config

        try:
            DataSourceSyncConfig(**sync_config)
        except PDValidationError as e:
            raise ValidationError(_("同步配置不合法：{}").format(stringify_pydantic_error(e)))

        return sync_config

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # 除本地数据源类型外，都需要配置字段映射
        if attrs["plugin_id"] != DataSourcePluginEnum.LOCAL and not attrs["field_mapping"]:
            raise ValidationError(_("当前数据源类型必须配置字段映射"))

        PluginConfigCls = get_plugin_cfg_cls(attrs["plugin_id"])  # noqa: N806
        # 自定义插件，可能没有对应的配置类，不需要做格式检查
        if not PluginConfigCls:
            return attrs

        try:
            PluginConfigCls(**attrs["plugin_config"])
        except PDValidationError as e:
            raise ValidationError(_("插件配置不合法：{}").format(stringify_pydantic_error(e)))

        return attrs


class DataSourceCreateOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="数据源 ID")


class DataSourcePluginOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="数据源插件唯一标识")
    name = serializers.CharField(help_text="数据源插件名称")
    description = serializers.CharField(help_text="数据源插件描述")
    logo = serializers.CharField(help_text="数据源插件 Logo")


class DataSourcePluginDefaultConfigOutputSLZ(serializers.Serializer):
    config = serializers.JSONField(help_text="数据源插件默认配置")


class DataSourceRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="数据源 ID")
    name = serializers.CharField(help_text="数据源名称")
    owner_tenant_id = serializers.CharField(help_text="数据源所属租户 ID")
    status = serializers.CharField(help_text="数据源状态")
    plugin = DataSourcePluginOutputSLZ(help_text="数据源插件")
    plugin_config = serializers.JSONField(help_text="数据源插件配置")
    sync_config = serializers.JSONField(help_text="数据源同步任务配置")
    field_mapping = serializers.JSONField(help_text="用户字段映射")


class DataSourceUpdateInputSLZ(serializers.Serializer):
    plugin_config = serializers.JSONField(help_text="数据源插件配置")
    field_mapping = serializers.ListField(
        help_text="用户字段映射", child=DataSourceFieldMappingSLZ(), allow_empty=True, required=False, default=list
    )
    sync_config = serializers.JSONField(help_text="数据源同步配置", default=dict)

    def validate_plugin_config(self, plugin_config: Dict[str, Any]) -> Dict[str, Any]:
        PluginConfigCls = get_plugin_cfg_cls(self.context["plugin_id"])  # noqa: N806
        # 自定义插件，可能没有对应的配置类，不需要做格式检查
        if not PluginConfigCls:
            return plugin_config

        try:
            PluginConfigCls(**plugin_config)
        except PDValidationError as e:
            raise ValidationError(_("插件配置不合法：{}").format(stringify_pydantic_error(e)))

        return plugin_config

    def validate_field_mapping(self, field_mapping: List[Dict]) -> List[Dict]:
        # 除本地数据源类型外，都需要配置字段映射
        if self.context["plugin_id"] == DataSourcePluginEnum.LOCAL:
            return field_mapping

        if not field_mapping:
            raise ValidationError(_("当前数据源类型必须配置字段映射"))

        target_fields = {m.get("target_field") for m in field_mapping}
        allowed_target_fields = list(UserBuiltinField.objects.all().values_list("name", flat=True)) + list(
            TenantUserCustomField.objects.filter(tenant_id=self.context["tenant_id"]).values_list("name", flat=True)
        )
        if not_allowed_fields := target_fields - set(allowed_target_fields):
            raise ValidationError(
                _("字段映射中的目标字段 {} 不属于用户自定义字段或内置字段").format(not_allowed_fields),
            )

        return field_mapping

    def validate_sync_config(self, sync_config: Dict[str, Any]) -> Dict[str, Any]:
        if not sync_config:
            return sync_config

        try:
            DataSourceSyncConfig(**sync_config)
        except PDValidationError as e:
            raise ValidationError(_("同步配置不合法：{}").format(stringify_pydantic_error(e)))

        return sync_config


class DataSourceSwitchStatusOutputSLZ(serializers.Serializer):
    status = serializers.CharField(help_text="数据源状态")


class RawDataSourceUserSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    properties = serializers.JSONField(help_text="用户属性")
    leaders = serializers.ListField(help_text="用户 leader ID 列表", child=serializers.CharField())
    departments = serializers.ListField(help_text="用户部门 ID 列表", child=serializers.CharField())


class RawDataSourceDepartmentSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="部门 ID")
    name = serializers.CharField(help_text="部门名称")
    parent = serializers.CharField(help_text="父部门 ID")


class DataSourceTestConnectionOutputSLZ(serializers.Serializer):
    """数据源连通性测试"""

    error_message = serializers.CharField(help_text="错误信息")
    user = RawDataSourceUserSLZ(help_text="用户")
    department = RawDataSourceDepartmentSLZ(help_text="部门")


class LocalDataSourceImportInputSLZ(serializers.Serializer):
    """本地数据源导入"""

    file = serializers.FileField(help_text="数据源用户信息文件（Excel 格式）")
    overwrite = serializers.BooleanField(help_text="允许对同名用户覆盖更新", default=False)
    incremental = serializers.BooleanField(help_text="是否使用增量同步", default=False)


class LocalDataSourceImportOutputSLZ(serializers.Serializer):
    """本地数据源导入结果"""

    task_id = serializers.CharField(help_text="任务 ID")
    status = serializers.CharField(help_text="任务状态")
    summary = serializers.CharField(help_text="任务执行结果概述")
