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
from typing import Any, Dict, List

import pydantic
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.sync.models import TenantSyncTask
from bkuser.apps.tenant.data_models import CollaborativeStrategySourceConfig, CollaborativeStrategyTargetConfig
from bkuser.apps.tenant.models import CollaborativeStrategy, Tenant, TenantUserCustomField
from bkuser.utils.pydantic import stringify_pydantic_error


class CollaborativeToStrategyListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="协同策略 ID")
    name = serializers.CharField(help_text="协同策略名称")
    target_tenant_id = serializers.CharField(help_text="目标租户 ID")
    target_tenant_name = serializers.SerializerMethodField(help_text="目标租户名称")
    creator = serializers.SerializerMethodField(help_text="创建人")
    created_at = serializers.SerializerMethodField(help_text="创建时间")
    status = serializers.CharField(help_text="策略状态", source="source_status")
    config = serializers.JSONField(help_text="策略配置", source="source_config")

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_target_tenant_name(self, obj: CollaborativeStrategy) -> str:
        return self.context["tenant_name_map"][obj.target_tenant_id]

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_creator(self, obj: CollaborativeStrategy) -> str:
        return self.context["user_display_name_map"][obj.creator]

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_created_at(self, obj: CollaborativeStrategy) -> str:
        return obj.created_at_display


class CollaborativeFromStrategyListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="协同策略 ID")
    source_tenant_id = serializers.CharField(help_text="源租户 ID")
    source_tenant_name = serializers.SerializerMethodField(help_text="源租户名称")
    updated_at = serializers.SerializerMethodField(help_text="最近更新时间")
    status = serializers.CharField(help_text="策略状态", source="target_status")
    source_config = serializers.JSONField(help_text="策略配置（分享方）")
    target_config = serializers.JSONField(help_text="策略配置（接受方）")

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_source_tenant_name(self, obj: CollaborativeStrategy) -> str:
        return self.context["tenant_name_map"][obj.source_tenant_id]

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_updated_at(self, obj: CollaborativeStrategy) -> str:
        return obj.updated_at_display


class CollaborativeStrategyCreateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="协同策略名称")
    target_tenant_id = serializers.CharField(help_text="目标租户 ID")
    config = serializers.JSONField(help_text="策略配置")

    def validate_name(self, name: str) -> str:
        if CollaborativeStrategy.objects.filter(name=name, source_tenant_id=self.context["tenant_id"]).exists():
            raise ValidationError(_("同名协同策略已存在"))

        return name

    def validate_target_tenant_id(self, target_tenant_id: int) -> int:
        if target_tenant_id == self.context["tenant_id"]:
            raise ValidationError(_("目标租户不能是当前租户"))

        if not Tenant.objects.filter(id=target_tenant_id).exists():
            raise ValidationError(_("目标租户不存在"))

        return target_tenant_id

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            CollaborativeStrategySourceConfig(**config)
        except pydantic.ValidationError as e:
            raise ValidationError(_("策略配置不合法：{}").format(stringify_pydantic_error(e)))

        return config


class CollaborativeStrategyCreateOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="协同策略 ID")


class CollaborativeStrategyUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="协同策略名称")
    config = serializers.JSONField(help_text="策略配置（分享方）")

    def validate_name(self, name: str) -> str:
        if (
            CollaborativeStrategy.objects.filter(name=name, source_tenant_id=self.context["tenant_id"])
            .exclude(id=self.context["strategy_id"])
            .exists()
        ):
            raise ValidationError(_("同名协同策略已存在"))

        return name

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            CollaborativeStrategySourceConfig(**config)
        except pydantic.ValidationError as e:
            raise ValidationError(_("策略配置不合法：{}").format(stringify_pydantic_error(e)))

        return config


def _validate_field_mapping_with_tenant_user_fields(
    field_mapping: List[Dict[str, str]], tenant_id: str
) -> List[Dict[str, str]]:
    target_fields = {m.get("target_field") for m in field_mapping}

    custom_fields = TenantUserCustomField.objects.filter(tenant_id=tenant_id)
    if not_allowed_fields := target_fields - set(custom_fields.values_list("name", flat=True)):
        raise ValidationError(
            _("字段映射中的目标字段 {} 不属于租户用户自定义字段").format(not_allowed_fields),
        )

    required_target_fields = set(custom_fields.filter(required=True).values_list("name", flat=True))
    if missed_required_fields := required_target_fields - target_fields:
        raise ValidationError(_("必填目标字段 {} 缺少字段映射").format(missed_required_fields))

    return field_mapping


class CollaborativeStrategyConfirmInputSLZ(serializers.Serializer):
    config = serializers.JSONField(help_text="策略配置（接受方）")

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            CollaborativeStrategyTargetConfig(**config)
        except pydantic.ValidationError as e:
            raise ValidationError(_("策略配置不合法：{}").format(stringify_pydantic_error(e)))

        _validate_field_mapping_with_tenant_user_fields(config["field_mapping"], self.context["tenant_id"])
        return config


class CollaborativeStrategyStatusUpdateOutputSLZ(serializers.Serializer):
    status = serializers.CharField(help_text="策略状态")


class CollaborativeSyncRecordListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="同步记录 ID")
    source_tenant_id = serializers.CharField(help_text="源租户 ID", source="data_source.owner_tenant_id")
    source_tenant_name = serializers.SerializerMethodField(help_text="源租户名称")
    has_warning = serializers.BooleanField(help_text="是否有警告")
    status = serializers.CharField(help_text="同步状态")
    start_at = serializers.DateTimeField(help_text="创建时间")
    duration = serializers.DurationField(help_text="持续时间")
    summary = serializers.JSONField(help_text="任务执行概述")

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_source_tenant_name(self, obj: TenantSyncTask) -> str:
        return self.context["tenant_name_map"][obj.data_source.owner_tenant_id]