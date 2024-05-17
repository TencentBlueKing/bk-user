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

from bkuser.apps.sync.constants import SyncOperation, SyncTaskStatus
from bkuser.apps.sync.models import (
    DataSourceDepartmentChangeLog,
    DataSourceUserChangeLog,
    TenantDepartmentChangeLog,
    TenantSyncTask,
    TenantUserChangeLog,
)
from bkuser.apps.tenant.constants import CollaborationStrategyStatus, UserFieldDataType
from bkuser.apps.tenant.data_models import CollaborationStrategySourceConfig, CollaborationStrategyTargetConfig
from bkuser.apps.tenant.models import CollaborationStrategy, Tenant, TenantUserCustomField
from bkuser.utils.pydantic import stringify_pydantic_error

# ---------------------------------- 分享方 SLZ ----------------------------------


class CollaborationToStrategyListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="协同策略 ID")
    name = serializers.CharField(help_text="协同策略名称")
    target_tenant_id = serializers.CharField(help_text="目标租户 ID")
    target_tenant_name = serializers.SerializerMethodField(help_text="目标租户名称")
    creator = serializers.SerializerMethodField(help_text="创建人")
    created_at = serializers.DateTimeField(help_text="创建时间")
    source_status = serializers.ChoiceField(
        help_text="策略状态（分享方）",
        choices=CollaborationStrategyStatus.get_choices(),
    )
    source_config = serializers.JSONField(help_text="策略配置（分享方）")

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_target_tenant_name(self, obj: CollaborationStrategy) -> str:
        return self.context["tenant_name_map"][obj.target_tenant_id]

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_creator(self, obj: CollaborationStrategy) -> str:
        return self.context["user_display_name_map"][obj.creator]


class CollaborationToStrategyCreateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="协同策略名称")
    target_tenant_id = serializers.CharField(help_text="目标租户 ID")
    source_config = serializers.JSONField(help_text="策略配置")

    def validate_name(self, name: str) -> str:
        if CollaborationStrategy.objects.filter(name=name, source_tenant_id=self.context["tenant_id"]).exists():
            raise ValidationError(_("同名协同策略已存在"))

        return name

    def validate_target_tenant_id(self, target_tenant_id: int) -> int:
        if target_tenant_id == self.context["tenant_id"]:
            raise ValidationError(_("目标租户不能是当前租户"))

        if not Tenant.objects.filter(id=target_tenant_id).exists():
            raise ValidationError(_("目标租户不存在"))

        return target_tenant_id

    def validate_source_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            CollaborationStrategySourceConfig(**config)
        except pydantic.ValidationError as e:
            raise ValidationError(_("策略配置不合法：{}").format(stringify_pydantic_error(e)))

        return config

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if CollaborationStrategy.objects.filter(
            source_tenant=self.context["tenant_id"], target_tenant_id=attrs["target_tenant_id"]
        ).exists():
            raise ValidationError(_("当前租户到租户 {} 的协同策略已存在").format(attrs["target_tenant_id"]))
        return attrs


class CollaborationToStrategyCreateOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="协同策略 ID")


class CollaborationToStrategyUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="协同策略名称")
    source_config = serializers.JSONField(help_text="策略配置（分享方）")

    def validate_name(self, name: str) -> str:
        if (
            CollaborationStrategy.objects.filter(name=name, source_tenant_id=self.context["tenant_id"])
            .exclude(id=self.context["strategy_id"])
            .exists()
        ):
            raise ValidationError(_("同名协同策略已存在"))

        return name

    def validate_source_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            CollaborationStrategySourceConfig(**config)
        except pydantic.ValidationError as e:
            raise ValidationError(_("策略配置不合法：{}").format(stringify_pydantic_error(e)))

        return config


class CollaborationToStrategySourceStatusUpdateOutputSLZ(serializers.Serializer):
    source_status = serializers.ChoiceField(help_text="策略状态", choices=CollaborationStrategyStatus.get_choices())


# ---------------------------------- 接受方 SLZ ----------------------------------


class CollaborationFromStrategyListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="协同策略 ID")
    source_tenant_id = serializers.CharField(help_text="源租户 ID")
    source_tenant_name = serializers.SerializerMethodField(help_text="源租户名称")
    updated_at = serializers.DateTimeField(help_text="最近更新时间")
    target_status = serializers.ChoiceField(
        help_text="策略状态（接受方）",
        choices=CollaborationStrategyStatus.get_choices(),
    )
    source_config = serializers.JSONField(help_text="策略配置（分享方）")
    target_config = serializers.JSONField(help_text="策略配置（接受方）")

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_source_tenant_name(self, obj: CollaborationStrategy) -> str:
        return self.context["tenant_name_map"][obj.source_tenant_id]


class CollaborationSourceTenantCustomFieldListOutputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="英文标识")
    display_name = serializers.CharField(help_text="展示用名称")
    data_type = serializers.ChoiceField(help_text="字段类型", choices=UserFieldDataType.get_choices())


def _validate_field_mapping_with_tenant_user_fields(
    field_mapping: List[Dict[str, str]], source_tenant_id: str, target_tenant_id: str
):
    """校验协同策略中的字段映射，是否能匹配源 / 目标租户的自定义字段"""

    source_tenant_custom_field_map = {
        f.name: f for f in TenantUserCustomField.objects.filter(tenant_id=source_tenant_id)
    }
    target_tenant_custom_field_map = {
        f.name: f for f in TenantUserCustomField.objects.filter(tenant_id=target_tenant_id)
    }

    # 源字段检查（是否合法）
    source_fields = {m.get("source_field") for m in field_mapping}
    if not_allowed_fields := source_fields - set(source_tenant_custom_field_map.keys()):
        raise ValidationError(_("字段映射中的源字段 {} 不属于源租户用户自定义字段").format(not_allowed_fields))

    # 目标字段检查（是否合法） 注：不需要检查必填字段是否已配置
    target_fields = {m.get("target_field") for m in field_mapping}
    if not_allowed_fields := target_fields - set(target_tenant_custom_field_map.keys()):
        raise ValidationError(
            _("字段映射中的目标字段 {} 不属于本租户用户自定义字段").format(not_allowed_fields),
        )

    for mp in field_mapping:
        source_field = source_tenant_custom_field_map[mp["source_field"]]
        target_field = target_tenant_custom_field_map[mp["target_field"]]
        # 字段类型检查
        if source_field.data_type != target_field.data_type:
            raise ValidationError(
                _("字段映射中的源字段 {} 和 目标字段 {} 的类型不一致").format(mp["source_field"], mp["target_field"]),
            )

        # 如果是枚举类型，还要校验枚举值是否一致（字面值可以不一致）
        # TODO (su) 评估策略创建后，某一方修改枚举值的影响？
        if source_field.data_type in [UserFieldDataType.ENUM, UserFieldDataType.MULTI_ENUM]:  # noqa: SIM102
            if {opt["id"] for opt in source_field.options} != {opt["id"] for opt in target_field.options}:
                raise ValidationError(
                    _(
                        "字段映射中的源字段 {} 和 目标字段 {} 的枚举值不一致",
                    ).format(mp["source_field"], mp["target_field"]),
                )


class CollaborationFromStrategyUpdateInputSLZ(serializers.Serializer):
    target_config = serializers.JSONField(help_text="策略配置（接受方）")

    def validate_target_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            CollaborationStrategyTargetConfig(**config)
        except pydantic.ValidationError as e:
            raise ValidationError(_("策略配置不合法：{}").format(stringify_pydantic_error(e)))

        _validate_field_mapping_with_tenant_user_fields(
            config["field_mapping"], self.context["source_tenant_id"], self.context["target_tenant_id"]
        )
        return config


class CollaborationFromStrategyConfirmInputSLZ(CollaborationFromStrategyUpdateInputSLZ):
    ...


class CollaborationFromStrategyTargetStatusUpdateOutputSLZ(serializers.Serializer):
    target_status = serializers.ChoiceField(help_text="策略状态", choices=CollaborationStrategyStatus.get_choices())


class CollaborationSyncRecordListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="同步记录 ID")
    source_tenant_id = serializers.CharField(help_text="源租户 ID", source="data_source.owner_tenant_id")
    source_tenant_name = serializers.SerializerMethodField(help_text="源租户名称")
    has_warning = serializers.BooleanField(help_text="是否有警告")
    status = serializers.ChoiceField(help_text="同步状态", choices=SyncTaskStatus.get_choices())
    start_at = serializers.DateTimeField(help_text="创建时间")
    duration = serializers.DurationField(help_text="持续时间")
    summary = serializers.JSONField(help_text="任务执行概述")

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_source_tenant_name(self, obj: TenantSyncTask) -> str:
        return self.context["tenant_name_map"][obj.data_source.owner_tenant_id]


def get_collaboration_objects_info(obj: TenantSyncTask, operation: SyncOperation) -> Dict[str, Any]:
    # 记录中只会保留租户用户 & 数据源用户 ID，需要查询对应的数据源记录才可以拿到用户名
    # FIXME (su) 如果 obj.data_source_sync_task_id 为 0 会拿不到数据，需要看下怎么处理比较合适
    tenant_user_change_logs = TenantUserChangeLog.objects.filter(task_id=obj.id, operation=operation)
    data_source_user_ids = [cl.data_source_user_id for cl in tenant_user_change_logs[:50]]
    data_source_user_change_logs = DataSourceUserChangeLog.objects.filter(
        task_id=obj.data_source_sync_task_id, user_id__in=data_source_user_ids
    )

    # 记录中只会保留租户部门 & 数据源部门 ID，需要查询对应的数据源记录才可以拿到部门名称
    tenant_dept_change_logs = TenantDepartmentChangeLog.objects.filter(task_id=obj.id, operation=operation)
    data_source_dept_ids = [cl.data_source_department_id for cl in tenant_dept_change_logs[:50]]
    data_source_dept_change_logs = DataSourceDepartmentChangeLog.objects.filter(
        task_id=obj.data_source_sync_task_id, department_id__in=data_source_dept_ids
    )

    return {
        "user_count": tenant_user_change_logs.count(),
        "usernames": [f"{cl.username}({cl.full_name})" for cl in data_source_user_change_logs],
        "department_count": tenant_dept_change_logs.count(),
        "department_names": [cl.department_name for cl in data_source_dept_change_logs],
    }


class CollaborationObjectsSLZ(serializers.Serializer):
    user_count = serializers.IntegerField(help_text="用户数量")
    usernames = serializers.ListField(help_text="用户列表", child=serializers.CharField())
    department_count = serializers.IntegerField(help_text="部门数量")
    department_names = serializers.ListField(help_text="部门列表", child=serializers.CharField())


class CollaborationSyncRecordRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="同步记录 ID")
    status = serializers.ChoiceField(help_text="同步状态", choices=SyncTaskStatus.get_choices())
    has_warning = serializers.BooleanField(help_text="是否有警告")
    start_at = serializers.DateTimeField(help_text="创建时间")
    duration = serializers.DurationField(help_text="持续时间")
    logs = serializers.CharField(help_text="同步日志")
    created_objs = serializers.SerializerMethodField(help_text="创建的对象")
    deleted_objs = serializers.SerializerMethodField(help_text="删除的对象")

    @swagger_serializer_method(serializer_or_field=CollaborationObjectsSLZ())
    def get_created_objs(self, obj: TenantSyncTask) -> Dict[str, Any]:
        return CollaborationObjectsSLZ(get_collaboration_objects_info(obj, SyncOperation.CREATE)).data

    @swagger_serializer_method(serializer_or_field=CollaborationObjectsSLZ())
    def get_deleted_objs(self, obj: TenantSyncTask) -> Dict[str, Any]:
        return CollaborationObjectsSLZ(get_collaboration_objects_info(obj, SyncOperation.DELETE)).data
