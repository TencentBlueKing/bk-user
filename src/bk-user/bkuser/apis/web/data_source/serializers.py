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

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_serializer_method
from pydantic import ValidationError as PDValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import FieldMappingOperation
from bkuser.apps.data_source.models import DataSource, DataSourcePlugin, DataSourceSensitiveInfo
from bkuser.apps.sync.constants import DataSourceSyncPeriod, SyncTaskStatus, SyncTaskTrigger
from bkuser.apps.sync.models import DataSourceSyncTask
from bkuser.apps.tenant.models import TenantUserCustomField, UserBuiltinField
from bkuser.biz.data_source_plugin import DefaultPluginConfigProvider
from bkuser.common.constants import SENSITIVE_MASK
from bkuser.plugins.base import get_plugin_cfg_cls, is_plugin_exists
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import PasswordRuleConfig
from bkuser.plugins.models import BasePluginConfig
from bkuser.utils import dictx
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


def _validate_field_mapping_with_tenant_user_fields(
    field_mapping: List[Dict[str, str]], tenant_id: str
) -> List[Dict[str, str]]:
    target_fields = {m.get("target_field") for m in field_mapping}

    builtin_fields = set(UserBuiltinField.objects.all().values_list("name", flat=True))
    tenant_user_custom_fields = TenantUserCustomField.objects.filter(tenant_id=tenant_id)

    allowed_target_fields = builtin_fields | set(tenant_user_custom_fields.values_list("name", flat=True))
    required_target_fields = builtin_fields | set(
        tenant_user_custom_fields.filter(required=True).values_list("name", flat=True)
    )

    if not_allowed_fields := target_fields - allowed_target_fields:
        raise ValidationError(
            _("字段映射中的目标字段 {} 不属于用户自定义字段或内置字段").format(not_allowed_fields),
        )
    if missed_required_fields := required_target_fields - target_fields:
        raise ValidationError(_("必填目标字段 {} 缺少字段映射").format(missed_required_fields))

    return field_mapping


class DataSourceSyncConfigSLZ(serializers.Serializer):
    """数据源同步配置"""

    sync_period = serializers.ChoiceField(help_text="同步周期", choices=DataSourceSyncPeriod.get_choices())


class DataSourceCreateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="数据源名称", max_length=128)
    plugin_id = serializers.CharField(help_text="数据源插件 ID")
    plugin_config = serializers.JSONField(help_text="数据源插件配置")
    field_mapping = serializers.ListField(
        help_text="用户字段映射", child=DataSourceFieldMappingSLZ(), allow_empty=True, required=False, default=list
    )
    sync_config = DataSourceSyncConfigSLZ(help_text="数据源同步配置", required=False)

    def validate_name(self, name: str) -> str:
        if DataSource.objects.filter(name=name).exists():
            raise ValidationError(_("同名数据源已存在"))

        return name

    def validate_plugin_id(self, plugin_id: str) -> str:
        if not DataSourcePlugin.objects.filter(id=plugin_id).exists():
            raise ValidationError(_("数据源插件不存在"))

        return plugin_id

    def validate_field_mapping(self, field_mapping: List[Dict[str, str]]) -> List[Dict[str, str]]:
        # 遇到空的字段映射，直接返回即可，validate() 中会根据插件类型校验是否必须提供字段映射
        if not field_mapping:
            return field_mapping

        return _validate_field_mapping_with_tenant_user_fields(field_mapping, self.context["tenant_id"])

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # 除本地数据源类型外，都需要配置字段映射
        plugin_id = attrs["plugin_id"]
        if plugin_id != DataSourcePluginEnum.LOCAL:
            if not attrs["field_mapping"]:
                raise ValidationError(_("当前数据源类型必须配置字段映射"))

            if not attrs.get("sync_config"):
                raise ValidationError(_("当前数据源类型必须提供同步配置"))

        if not is_plugin_exists(plugin_id):
            raise ValidationError(_("数据源插件 {} 不存在").format(plugin_id))

        PluginConfigCls = get_plugin_cfg_cls(plugin_id)  # noqa: N806
        try:
            attrs["plugin_config"] = PluginConfigCls(**attrs["plugin_config"])
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
    name = serializers.CharField(help_text="数据源名称", max_length=128)
    plugin_config = serializers.JSONField(help_text="数据源插件配置")
    field_mapping = serializers.ListField(
        help_text="用户字段映射", child=DataSourceFieldMappingSLZ(), allow_empty=True, required=False, default=list
    )
    sync_config = DataSourceSyncConfigSLZ(help_text="数据源同步配置", required=False)

    def validate_name(self, name: str) -> str:
        # 自己目前在用的名字是可以的，不然每次更新都要修改名字
        if name == self.context["current_name"]:
            return name

        if DataSource.objects.filter(name=name).exists():
            raise ValidationError(_("同名数据源已存在"))

        return name

    def validate_plugin_config(self, plugin_config: Dict[str, Any]) -> BasePluginConfig:
        PluginConfigCls = get_plugin_cfg_cls(self.context["plugin_id"])  # noqa: N806

        # 将敏感信息填充回 plugin_config，一并进行校验
        for info in self.context["exists_sensitive_infos"]:
            if dictx.get_items(plugin_config, info.key) == SENSITIVE_MASK:
                dictx.set_items(plugin_config, info.key, info.value)

        try:
            return PluginConfigCls(**plugin_config)
        except PDValidationError as e:
            raise ValidationError(_("插件配置不合法：{}").format(stringify_pydantic_error(e)))

    def validate_field_mapping(self, field_mapping: List[Dict[str, str]]) -> List[Dict[str, str]]:
        # 遇到空的字段映射，直接返回即可，validate() 中会根据插件类型校验是否必须提供字段映射
        if not field_mapping:
            return field_mapping

        return _validate_field_mapping_with_tenant_user_fields(field_mapping, self.context["tenant_id"])

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if self.context["plugin_id"] != DataSourcePluginEnum.LOCAL:
            if not attrs["field_mapping"]:
                raise ValidationError(_("当前数据源类型必须配置字段映射"))

            if not attrs.get("sync_config"):
                raise ValidationError(_("当前数据源类型必须提供同步配置"))

        return attrs


class DataSourceSwitchStatusOutputSLZ(serializers.Serializer):
    status = serializers.CharField(help_text="数据源状态")


class RawDataSourceUserSLZ(serializers.Serializer):
    code = serializers.CharField(help_text="用户 Code")
    properties = serializers.JSONField(help_text="用户属性")
    leaders = serializers.ListField(help_text="用户 leader code 列表", child=serializers.CharField())
    departments = serializers.ListField(help_text="用户部门 code 列表", child=serializers.CharField())


class RawDataSourceDepartmentSLZ(serializers.Serializer):
    code = serializers.CharField(help_text="部门 Code")
    name = serializers.CharField(help_text="部门名称")
    parent = serializers.CharField(help_text="父部门 Code")


class DataSourceTestConnectionInputSLZ(serializers.Serializer):
    data_source_id = serializers.IntegerField(help_text="数据源 ID（仅更新时候需要）", required=False)
    plugin_id = serializers.CharField(help_text="数据源插件 ID")
    plugin_config = serializers.JSONField(help_text="数据源插件配置")

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        plugin_id = attrs["plugin_id"]

        if plugin_id == DataSourcePluginEnum.LOCAL:
            raise ValidationError(_("本地数据源不支持连通性测试"))

        if not is_plugin_exists(plugin_id):
            raise ValidationError(_("数据源插件 {} 不存在").format(plugin_id))

        plugin_config = attrs["plugin_config"]

        if data_source_id := attrs.get("data_source_id"):
            # 若是更新场景，前端可以通过提供数据源 ID，这里将检查提供的数据源是否属于当前用户所在租户
            if not DataSource.objects.filter(id=data_source_id, owner_tenant_id=self.context["tenant_id"]).exists():
                raise ValidationError(
                    _("当前用户租户 {} 不存在 ID 为 {} 的数据源").format(self.context["tenant_id"], data_source_id),
                )

            # 若通过了数据源租户检查，则允许将 DB 中存在的敏感信息填充到配置中，并进行校验
            for info in DataSourceSensitiveInfo.objects.filter(data_source_id=data_source_id):
                if dictx.get_items(plugin_config, info.key) == SENSITIVE_MASK:
                    dictx.set_items(plugin_config, info.key, info.value)

        PluginConfigCls = get_plugin_cfg_cls(plugin_id)  # noqa: N806
        try:
            attrs["plugin_config"] = PluginConfigCls(**plugin_config)
        except PDValidationError as e:
            raise ValidationError(_("插件配置不合法：{}").format(stringify_pydantic_error(e)))

        return attrs


class DataSourceTestConnectionOutputSLZ(serializers.Serializer):
    error_message = serializers.CharField(help_text="错误信息")
    user = RawDataSourceUserSLZ(help_text="用户")
    department = RawDataSourceDepartmentSLZ(help_text="部门")
    extras = serializers.JSONField(help_text="额外信息")


class DataSourceRandomPasswordInputSLZ(serializers.Serializer):
    """生成随机密码"""

    password_rule_config = serializers.JSONField(help_text="密码规则配置", required=False)

    def validate(self, attrs):
        passwd_rule_cfg = attrs.get("password_rule_config")
        if passwd_rule_cfg:
            try:
                attrs["password_rule"] = PasswordRuleConfig(**passwd_rule_cfg).to_rule()
            except PDValidationError as e:
                raise ValidationError(_("密码规则配置不合法: {}").format(stringify_pydantic_error(e)))
        else:
            attrs["password_rule"] = (
                DefaultPluginConfigProvider().get(DataSourcePluginEnum.LOCAL).password_rule.to_rule()  # type: ignore
            )

        return attrs


class DataSourceRandomPasswordOutputSLZ(serializers.Serializer):
    """生成随机密码结果"""

    password = serializers.CharField(help_text="密码")


class LocalDataSourceImportInputSLZ(serializers.Serializer):
    """本地数据源导入"""

    file = serializers.FileField(help_text="数据源用户信息文件（Excel 格式）")
    overwrite = serializers.BooleanField(help_text="允许对同名用户覆盖更新", default=False)
    incremental = serializers.BooleanField(help_text="是否使用增量同步", default=True)

    def validate_file(self, file: UploadedFile) -> UploadedFile:
        if not file.name.endswith(".xlsx"):
            raise ValidationError(_("待导入文件必须为 Excel 格式"))

        if file.size > settings.MAX_USER_DATA_FILE_SIZE * 1024 * 1024:
            raise ValidationError(_("待导入文件大小不得超过 {} M").format(settings.MAX_USER_DATA_FILE_SIZE))

        return file


class DataSourceImportOrSyncOutputSLZ(serializers.Serializer):
    """数据源导入/同步结果"""

    task_id = serializers.CharField(help_text="任务 ID")
    status = serializers.CharField(help_text="任务状态")
    summary = serializers.CharField(help_text="任务执行结果概述")


class DataSourceSyncRecordSearchInputSLZ(serializers.Serializer):
    data_source_id = serializers.IntegerField(help_text="数据源 ID", required=False)
    status = serializers.ChoiceField(help_text="数据源同步状态", choices=SyncTaskStatus.get_choices(), required=False)


class DataSourceSyncRecordListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="同步记录 ID")
    data_source_id = serializers.IntegerField(help_text="数据源 ID")
    data_source_name = serializers.SerializerMethodField(help_text="数据源名称")
    status = serializers.ChoiceField(help_text="数据源同步状态", choices=SyncTaskStatus.get_choices())
    has_warning = serializers.BooleanField(help_text="是否有警告")
    trigger = serializers.ChoiceField(help_text="同步触发方式", choices=SyncTaskTrigger.get_choices())
    operator = serializers.CharField(help_text="操作人")
    start_at = serializers.SerializerMethodField(help_text="开始时间")
    duration = serializers.DurationField(help_text="持续时间")
    extras = serializers.JSONField(help_text="额外信息")

    def get_data_source_name(self, obj: DataSourceSyncTask) -> str:
        return self.context["data_source_name_map"].get(obj.data_source_id)

    def get_start_at(self, obj: DataSourceSyncTask) -> str:
        return obj.start_at_display


class DataSourceSyncRecordRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="同步记录 ID")
    status = serializers.CharField(help_text="数据源同步状态")
    has_warning = serializers.BooleanField(help_text="是否有警告")
    start_at = serializers.SerializerMethodField(help_text="开始时间")
    duration = serializers.DurationField(help_text="持续时间")
    logs = serializers.CharField(help_text="同步日志")

    def get_start_at(self, obj: DataSourceSyncTask) -> str:
        return obj.start_at_display
