# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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

import re
from typing import Any, Dict, List

from django.utils.translation import gettext_lazy as _
from pydantic import ValidationError as PDValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.idp.constants import IdpStatus
from bkuser.apps.idp.data_models import gen_field_compare_rules_of_local
from bkuser.apps.idp.models import Idp, IdpPlugin
from bkuser.apps.tenant.models import TenantUserCustomField, UserBuiltinField
from bkuser.biz.idp_data_source import IdpDataSourceRelationHandler
from bkuser.common.constants import SENSITIVE_MASK
from bkuser.idp_plugins.base import BasePluginConfig, get_plugin_cfg_cls
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.utils import dictx
from bkuser.utils.pydantic import stringify_pydantic_error


class IdpPluginOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源插件唯一标识")
    name = serializers.CharField(help_text="认证源插件名称")
    description = serializers.CharField(help_text="认证源插件描述")
    logo = serializers.CharField(help_text="认证源插件 Logo")


class IdpPluginConfigMetaRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源插件唯一标识")
    json_schema = serializers.JSONField(help_text="配置的 JSON Schema")


class IdpListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源唯一标识")
    status = serializers.ChoiceField(help_text="认证源状态", choices=IdpStatus.get_choices())
    plugin = IdpPluginOutputSLZ(help_text="认证源插件")


def _validate_duplicate_idp_name(name: str, tenant_id: str, idp_id: str = "") -> str:
    """校验 IDP 是否重名"""
    queryset = Idp.objects.filter(name=name, owner_tenant_id=tenant_id)
    # 过滤掉自身名称
    if idp_id:
        queryset = queryset.exclude(id=idp_id)

    if queryset.exists():
        raise ValidationError(_("同名认证源已存在"))

    return name


def _validate_duplicate_data_source_match_rules(data_source_match_rules: List[Dict[str, Any]]) -> None:
    """校验数据源匹配规则中的生效范围数据源 ID 不重复"""
    data_source_ids = [rule["data_source_id"] for rule in data_source_match_rules]
    if len(data_source_ids) != len(set(data_source_ids)):
        raise ValidationError(_("数据源匹配规则不能重复"))


def _validate_local_data_source_match_rules(tenant_id: str, data_source_match_rules: List[Dict[str, Any]]) -> None:
    """本地账密认证源的生效范围只允许选择已启用密码功能的本地实名数据源"""
    data_source_ids = {rule["data_source_id"] for rule in data_source_match_rules}

    local_data_sources = list(
        DataSource.objects.filter(
            id__in=data_source_ids,
            owner_tenant_id=tenant_id,
            type=DataSourceTypeEnum.REAL,
            plugin_id=DataSourcePluginEnum.LOCAL,
        )
    )
    if invalid_ids := data_source_ids - {data_source.id for data_source in local_data_sources}:
        raise ValidationError(_("本地认证源的生效范围仅允许选择本地实名数据源，不合法数据源：{}").format(invalid_ids))

    # 本地认证源依赖数据源的密码功能，未启用密码的数据源无法用于账密登录
    if password_disabled_ids := {
        data_source.id for data_source in local_data_sources if not data_source.get_plugin_cfg().enable_password
    }:
        raise ValidationError(
            _("本地认证源仅允许关联已启用密码功能的数据源，未启用数据源：{}").format(password_disabled_ids)
        )


SOURCE_FIELD_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{1,30}[a-zA-Z0-9]$")


def _validate_source_field(value: str) -> None:
    """校验认证源字段命名规则"""
    if not re.fullmatch(SOURCE_FIELD_REGEX, value):
        raise ValidationError(
            _(
                "{} 不符合认证源字段的命名规范：由 3-32 位字母、数字、下划线 (_)、连接符 (-) 字符组成，以字母开头并以字母或数字结尾",  # noqa: E501
            ).format(value),
        )


def _validate_field_compare_rules(
    tenant_id: str, plugin_id: str, data_source_match_rules: List[Dict[str, Any]]
) -> None:
    """根据认证源类型校验字段匹配规则"""
    if plugin_id == BuiltinIdpPluginEnum.LOCAL:
        _validate_local_field_compare_rules(data_source_match_rules)
        return

    builtin_fields = set(UserBuiltinField.objects.all().values_list("name", flat=True))
    custom_fields = set(TenantUserCustomField.objects.filter(tenant_id=tenant_id).values_list("name", flat=True))
    allowed_target_fields = builtin_fields | custom_fields

    for match_rule in data_source_match_rules:
        for compare_rule in match_rule["field_compare_rules"]:
            _validate_source_field(compare_rule["source_field"])
            if compare_rule["target_field"] not in allowed_target_fields:
                raise ValidationError(
                    _("匹配的数据源字段 {} 不属于用户自定义字段或内置字段").format(compare_rule["target_field"])
                )


def _validate_local_field_compare_rules(data_source_match_rules: List[Dict[str, Any]]) -> None:
    expected_rules = [rule.model_dump() for rule in gen_field_compare_rules_of_local()]
    for match_rule in data_source_match_rules:
        if match_rule["field_compare_rules"] != expected_rules:
            raise ValidationError(_("本地认证源的字段匹配规则固定为 id -> id"))


def _validate_data_source_match_rules(
    tenant_id: str, plugin_id: str, data_source_match_rules: List[Dict[str, Any]]
) -> None:
    """校验认证源的数据源匹配规则"""
    _validate_duplicate_data_source_match_rules(data_source_match_rules)

    if plugin_id == BuiltinIdpPluginEnum.LOCAL:
        _validate_local_data_source_match_rules(tenant_id, data_source_match_rules)

    _validate_field_compare_rules(tenant_id, plugin_id, data_source_match_rules)


class FieldCompareRuleSLZ(serializers.Serializer):
    source_field = serializers.CharField(help_text="认证源原始字段")
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

        return attrs


class IdpCreateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="认证源名称", max_length=128)
    status = serializers.ChoiceField(help_text="认证源状态", choices=IdpStatus.get_choices())
    plugin_id = serializers.CharField(help_text="认证源插件 ID")
    plugin_config = serializers.JSONField(help_text="认证源插件配置")
    data_source_match_rules = serializers.ListField(
        help_text="数据源匹配规则", child=DataSourceMatchRuleSLZ(), allow_empty=False
    )

    def validate_name(self, name: str) -> str:
        return _validate_duplicate_idp_name(name, self.context["tenant_id"])

    def validate_plugin_id(self, plugin_id: str) -> str:
        if not IdpPlugin.objects.filter(id=plugin_id).exists():
            raise ValidationError(_("认证源插件不存在"))

        return plugin_id

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        plugin_id = attrs["plugin_id"]

        # 同类型的数据源对同一类型插件只允许一个
        if IdpDataSourceRelationHandler.has_duplicate_plugin_real_relation(self.context["tenant_id"], plugin_id):
            raise ValidationError(_("{} 类型的认证源已存在").format(plugin_id))

        try:
            cfg_cls = get_plugin_cfg_cls(plugin_id)
        except NotImplementedError:
            raise ValidationError(_("认证源插件 {} 不存在").format(plugin_id))

        try:
            # 本地认证源无需插件配置，直接忽略
            attrs["plugin_config"] = (
                cfg_cls(**attrs["plugin_config"]) if plugin_id != BuiltinIdpPluginEnum.LOCAL else cfg_cls()
            )
        except PDValidationError as e:
            raise ValidationError(_("认证源插件配置不合法：{}").format(stringify_pydantic_error(e)))

        _validate_data_source_match_rules(self.context["tenant_id"], plugin_id, attrs["data_source_match_rules"])

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
    data_source_match_rules = serializers.SerializerMethodField(help_text="数据源匹配规则")
    callback_uri = serializers.CharField(help_text="回调地址")

    def get_data_source_match_rules(self, obj: Idp) -> List[Dict[str, Any]]:
        return [rule.model_dump() for rule in IdpDataSourceRelationHandler.get_real_match_rules(obj)]


class IdpPartialUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="认证源名称")

    def validate_name(self, name: str) -> str:
        return _validate_duplicate_idp_name(name, self.context["tenant_id"], self.context["idp_id"])


class IdpUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="认证源名称", max_length=128)
    status = serializers.ChoiceField(help_text="认证源状态", choices=IdpStatus.get_choices())
    plugin_config = serializers.JSONField(help_text="认证源插件配置")
    data_source_match_rules = serializers.ListField(
        help_text="数据源匹配规则", child=DataSourceMatchRuleSLZ(), allow_empty=False
    )

    def validate_name(self, name: str) -> str:
        return _validate_duplicate_idp_name(name, self.context["tenant_id"], self.context["idp_id"])

    def validate_plugin_config(self, plugin_config: Dict[str, Any]) -> BasePluginConfig:
        cfg_cls = get_plugin_cfg_cls(self.context["plugin_id"])

        # 本地认证源无需插件配置，直接忽略
        if self.context["plugin_id"] == BuiltinIdpPluginEnum.LOCAL:
            return cfg_cls()

        # 将敏感信息填充回 plugin_config，一并进行校验
        for info in self.context["exists_sensitive_infos"]:
            if dictx.get_items(plugin_config, info.key) == SENSITIVE_MASK:
                dictx.set_items(plugin_config, info.key, info.value)

        try:
            return cfg_cls(**plugin_config)
        except PDValidationError as e:
            raise ValidationError(_("认证源插件配置不合法：{}").format(stringify_pydantic_error(e)))

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        plugin_id = self.context["plugin_id"]
        _validate_data_source_match_rules(self.context["tenant_id"], plugin_id, attrs["data_source_match_rules"])

        return attrs


class IdpSwitchStatusOutputSLZ(serializers.Serializer):
    status = serializers.ChoiceField(help_text="认证源状态", choices=IdpStatus.get_choices())
