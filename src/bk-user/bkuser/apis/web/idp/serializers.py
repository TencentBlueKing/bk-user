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
from typing import Any, Dict, List

from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_serializer_method
from pydantic import ValidationError as PDValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.models import DataSource
from bkuser.apps.idp.constants import IdpStatus
from bkuser.apps.idp.models import Idp, IdpPlugin
from bkuser.apps.tenant.models import TenantUserCustomField, UserBuiltinField
from bkuser.idp_plugins.base import BasePluginConfig, get_plugin_cfg_cls
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.utils.pydantic import stringify_pydantic_error


class IdpPluginOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源插件唯一标识")
    name = serializers.CharField(help_text="认证源插件名称")
    description = serializers.CharField(help_text="认证源插件描述")
    logo = serializers.CharField(help_text="认证源插件 Logo")


class IdpPluginConfigMetaRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源插件唯一标识")
    json_schema = serializers.JSONField(help_text="配置的JSON Schema")


class IdpSearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", required=False)


class IdpSearchOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="认证源唯一标识")
    name = serializers.CharField(help_text="认证源名称")
    status = serializers.ChoiceField(help_text="认证源状态", choices=IdpStatus.get_choices())
    updater = serializers.CharField(help_text="更新者")
    updated_at = serializers.CharField(help_text="更新时间", source="updated_at_display")
    plugin = IdpPluginOutputSLZ(help_text="认证源插件")
    matched_data_sources = serializers.SerializerMethodField(help_text="匹配的数据源列表")

    @swagger_serializer_method(
        serializer_or_field=serializers.ListField(
            help_text="匹配的数据源",
            child=serializers.CharField(),
            allow_empty=True,
        )
    )
    def get_matched_data_sources(self, obj: Idp) -> List[str]:
        data_source_name_map = self.context["data_source_name_map"]

        return [
            data_source_name_map[r.data_source_id]
            for r in obj.data_source_match_rule_objs
            if r.data_source_id in data_source_name_map
        ]

    def get_updater(self, obj: Idp) -> str:
        if not obj.updater:
            return ""
        updater = self.context["tenant_manager_map"][obj.updater].data_source_user
        expression_factors = {
            "username": updater.username,
            "full_name": updater.full_name,
        }
        return self.context["display_name_expression"].format(**expression_factors)


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
                "{} 不符合认证源字段的命名规范: 由3-32位字母、数字、下划线(_)、连接符(-)字符组成，以字母开头并以字母或数字结尾"  # noqa: E501
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
        if not DataSource.objects.filter(id=attrs["data_source_id"], owner_tenant_id=tenant_id).exists():
            raise ValidationError(_("数据源必须是当前租户下的，{} 并不符合").format(attrs["data_source_id"]))

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
    plugin_id = serializers.CharField(help_text="认证源插件 ID")
    plugin_config = serializers.JSONField(help_text="认证源插件配置")
    data_source_match_rules = serializers.ListField(
        help_text="数据源匹配规则", child=DataSourceMatchRuleSLZ(), allow_empty=True, default=list
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
    owner_tenant_id = serializers.CharField(help_text="认证源所属租户 ID")
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
    plugin_config = serializers.JSONField(help_text="认证源插件配置")
    data_source_match_rules = serializers.ListField(
        help_text="数据源匹配规则", child=DataSourceMatchRuleSLZ(), allow_empty=True, default=list
    )

    def validate_name(self, name: str) -> str:
        return _validate_duplicate_idp_name(name, self.context["tenant_id"], self.context["idp_id"])

    def validate_plugin_config(self, plugin_config: Dict[str, Any]) -> BasePluginConfig:
        cfg_cls = get_plugin_cfg_cls(self.context["plugin_id"])

        try:
            return cfg_cls(**plugin_config)
        except PDValidationError as e:
            raise ValidationError(_("认证源插件配置不合法：{}").format(stringify_pydantic_error(e)))
