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
import re
from typing import Any, Dict

from django.utils.translation import gettext_lazy as _
from pydantic import ValidationError as PDValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.idp.constants import INVALID_REAL_DATA_SOURCE_ID, IdpStatus
from bkuser.apps.idp.models import Idp, IdpPlugin
from bkuser.apps.tenant.models import TenantUserCustomField, UserBuiltinField
from bkuser.common.constants import SENSITIVE_MASK
from bkuser.idp_plugins.base import BasePluginConfig, get_plugin_cfg_cls
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig
from bkuser.utils import dictx
from bkuser.utils.pydantic import stringify_pydantic_error


class IdpPluginOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源插件唯一标识")
    name = serializers.CharField(help_text="认证源插件名称")
    description = serializers.CharField(help_text="认证源插件描述")
    logo = serializers.CharField(help_text="认证源插件 Logo")


class IdpPluginConfigMetaRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源插件唯一标识")
    json_schema = serializers.JSONField(help_text="配置的JSON Schema")


class IdpListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源唯一标识")
    status = serializers.ChoiceField(help_text="认证源状态", choices=IdpStatus.get_choices())
    plugin = IdpPluginOutputSLZ(help_text="认证源插件")


def _validate_duplicate_idp_name(name: str, tenant_id: str, idp_id: str = "") -> str:
    """校验IDP 是否重名"""
    queryset = Idp.objects.filter(name=name, owner_tenant_id=tenant_id)
    # 过滤掉自身名称
    if idp_id:
        queryset = queryset.exclude(id=idp_id)

    if queryset.exists():
        raise ValidationError(_("同名认证源已存在"))

    return name


SOURCE_FIELD_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{1,30}[a-zA-Z0-9]$")


def _validate_source_field(value):
    """校验认证源字段命名规则"""
    if not re.fullmatch(SOURCE_FIELD_REGEX, value):
        raise ValidationError(
            _(
                "{} 不符合认证源字段的命名规范: 由3-32位字母、数字、下划线(_)、连接符(-)字符组成，以字母开头并以字母或数字结尾",  # noqa: E501
            ).format(value),
        )


class FieldCompareRuleSLZ(serializers.Serializer):
    source_field = serializers.CharField(help_text="认证源原始字段", validators=[_validate_source_field])
    target_field = serializers.CharField(help_text="匹配的数据源字段")


class DataSourceMatchRuleSLZ(serializers.Serializer):
    data_source_id = serializers.IntegerField(help_text="数据源 ID")
    field_compare_rules = serializers.ListField(
        help_text="字段比较规则", child=FieldCompareRuleSLZ(), allow_empty=False, min_length=1
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # 数据源是否当前租户的
        tenant_id = self.context["tenant_id"]
        if not DataSource.objects.filter(
            id=attrs["data_source_id"], owner_tenant_id=tenant_id, type=DataSourceTypeEnum.REAL
        ).exists():
            raise ValidationError(_("当前租户下不存在 ID 为 {} 的实名数据源").format(attrs["data_source_id"]))

        # 匹配的数据源字段必须是当前租户的用户字段，包括内建字段和自定义字段
        builtin_fields = set(UserBuiltinField.objects.all().values_list("name", flat=True))
        custom_fields = set(TenantUserCustomField.objects.filter(tenant_id=tenant_id).values_list("name", flat=True))
        allowed_target_fields = builtin_fields | custom_fields

        target_fields = {r.get("target_field") for r in attrs["field_compare_rules"]}
        if not_found_fields := target_fields - allowed_target_fields:
            raise ValidationError(_("匹配的数据源字段 {} 不属于用户自定义字段或内置字段").format(not_found_fields))

        return attrs


class IdpCreateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="认证源名称", max_length=128)
    status = serializers.ChoiceField(help_text="认证源状态", choices=IdpStatus.get_choices())
    plugin_id = serializers.CharField(help_text="认证源插件 ID")
    plugin_config = serializers.JSONField(help_text="认证源插件配置")
    data_source_match_rules = serializers.ListField(
        help_text="数据源匹配规则", child=DataSourceMatchRuleSLZ(), allow_empty=False, default=list
    )

    def validate_name(self, name: str) -> str:
        return _validate_duplicate_idp_name(name, self.context["tenant_id"])

    def validate_plugin_id(self, plugin_id: str) -> str:
        if not IdpPlugin.objects.filter(id=plugin_id).exists():
            raise ValidationError(_("认证源插件不存在"))

        if plugin_id == BuiltinIdpPluginEnum.LOCAL:
            raise ValidationError(_("不允许创建本地账密认证源"))

        return plugin_id

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        plugin_id = attrs["plugin_id"]

        # 同类型的数据源对同一类型插件只允许一个
        if Idp.objects.filter(
            owner_tenant_id=self.context["tenant_id"],
            plugin_id=plugin_id,
            data_source_id__in=[INVALID_REAL_DATA_SOURCE_ID, attrs["data_source_match_rules"][0]["data_source_id"]],
        ).exists():
            raise ValidationError(_("{} 类型的认证源已存在").format(plugin_id))

        try:
            cfg_cls = get_plugin_cfg_cls(plugin_id)
        except NotImplementedError:
            raise ValidationError(_("认证源插件 {} 不存在").format(plugin_id))

        try:
            attrs["plugin_config"] = cfg_cls(**attrs["plugin_config"])
        except PDValidationError as e:
            raise ValidationError(_("认证源插件配置不合法：{}").format(stringify_pydantic_error(e)))

        return attrs


class IdpCreateOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源 ID")
    callback_uri = serializers.CharField(help_text="回调地址")


class IdpRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源唯一标识")
    name = serializers.CharField(help_text="认证源名称")
    status = serializers.ChoiceField(help_text="认证源状态", choices=IdpStatus.get_choices())
    plugin = IdpPluginOutputSLZ(help_text="认证源插件")
    plugin_config = serializers.JSONField(help_text="认证源插件配置")
    data_source_match_rules = serializers.JSONField(help_text="数据源匹配规则", default=list)
    callback_uri = serializers.CharField(help_text="回调地址")


class IdpPartialUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="认证源名称")

    def validate_name(self, name: str) -> str:
        return _validate_duplicate_idp_name(name, self.context["tenant_id"], self.context["idp_id"])


class IdpUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="认证源名称", max_length=128)
    status = serializers.ChoiceField(help_text="认证源状态", choices=IdpStatus.get_choices())
    plugin_config = serializers.JSONField(help_text="认证源插件配置")
    data_source_match_rules = serializers.ListField(
        help_text="数据源匹配规则", child=DataSourceMatchRuleSLZ(), allow_empty=False, default=list
    )

    def validate_name(self, name: str) -> str:
        return _validate_duplicate_idp_name(name, self.context["tenant_id"], self.context["idp_id"])

    def validate_plugin_config(self, plugin_config: Dict[str, Any]) -> BasePluginConfig:
        cfg_cls = get_plugin_cfg_cls(self.context["plugin_id"])

        # 将敏感信息填充回 plugin_config，一并进行校验
        for info in self.context["exists_sensitive_infos"]:
            if dictx.get_items(plugin_config, info.key) == SENSITIVE_MASK:
                dictx.set_items(plugin_config, info.key, info.value)

        try:
            return cfg_cls(**plugin_config)
        except PDValidationError as e:
            raise ValidationError(_("认证源插件配置不合法：{}").format(stringify_pydantic_error(e)))


class IdpSwitchStatusOutputSLZ(serializers.Serializer):
    status = serializers.ChoiceField(help_text="认证源状态", choices=IdpStatus.get_choices())


class LocalIdpCreateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="认证源名称", max_length=128)
    status = serializers.ChoiceField(help_text="认证源状态", choices=IdpStatus.get_choices())
    # Note: 本地认证源的密码配置实际上是写入本地数据源的
    plugin_config = serializers.JSONField(help_text="本地数据源插件配置")

    def validate_name(self, name: str) -> str:
        return _validate_duplicate_idp_name(name, self.context["tenant_id"])

    def validate_plugin_config(self, plugin_config: Dict[str, Any]) -> LocalDataSourcePluginConfig:
        try:
            return LocalDataSourcePluginConfig(**plugin_config)
        except PDValidationError as e:
            raise ValidationError(_("认证源插件配置不合法：{}").format(stringify_pydantic_error(e)))

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        plugin_config = attrs["plugin_config"]
        assert isinstance(plugin_config, LocalDataSourcePluginConfig)

        status = attrs["status"]
        # 启动登录和启用密码功能必须保持一致
        if (plugin_config.enable_password and status == IdpStatus.DISABLED) or (
            not plugin_config.enable_password and status == IdpStatus.ENABLED
        ):
            raise ValidationError("本地登录启用状态必须与密码功能启用保持一致")

        return attrs


class LocalIdpRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源唯一标识")
    name = serializers.CharField(help_text="认证源名称")
    status = serializers.ChoiceField(help_text="认证源状态", choices=IdpStatus.get_choices())
    plugin_config = serializers.JSONField(help_text="本地数据源密码配置")


class LocalIdpUpdateInputSLZ(LocalIdpCreateInputSLZ):
    def validate_name(self, name: str) -> str:
        return _validate_duplicate_idp_name(name, self.context["tenant_id"], self.context["idp_id"])

    def validate_plugin_config(self, plugin_config: Dict[str, Any]) -> LocalDataSourcePluginConfig:
        # 将敏感信息填充回 plugin_config，一并进行校验
        for info in self.context["exists_sensitive_infos"]:
            if dictx.get_items(plugin_config, info.key) == SENSITIVE_MASK:
                dictx.set_items(plugin_config, info.key, info.value)

        return super().validate_plugin_config(plugin_config)
