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
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_serializer_method
from pydantic import ValidationError as PDValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import DataSourcePluginEnum, FieldMappingOperation
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentUserRelation,
    DataSourcePlugin,
    DataSourceUser,
)
from bkuser.apps.data_source.plugins.constants import DATA_SOURCE_PLUGIN_CONFIG_CLASS_MAP
from bkuser.biz.validators import validate_data_source_user_username
from bkuser.common.validators import validate_phone_with_country_code
from bkuser.utils.pydantic import stringify_pydantic_error

logger = logging.getLogger(__name__)


class DataSourceSearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", required=False)


class DataSourceSearchOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="数据源 ID")
    name = serializers.CharField(help_text="数据源名称")
    owner_tenant_id = serializers.CharField(help_text="数据源所属租户 ID")
    plugin_name = serializers.SerializerMethodField(help_text="数据源插件名称")
    collaborative_companies = serializers.SerializerMethodField(help_text="协作公司")
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
    def get_collaborative_companies(self, obj: DataSource) -> List[str]:
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

    def validate_plugin_id(self, plugin_id: str) -> str:
        if not DataSourcePlugin.objects.filter(id=plugin_id).exists():
            raise ValidationError(_("数据源插件不存在"))

        return plugin_id

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # 除本地数据源类型外，都需要配置字段映射
        if attrs["plugin_id"] != DataSourcePluginEnum.LOCAL and not attrs["field_mapping"]:
            raise ValidationError(_("当前数据源类型必须配置字段映射"))

        PluginConfigCls = DATA_SOURCE_PLUGIN_CONFIG_CLASS_MAP.get(attrs["plugin_id"])  # noqa: N806
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

    def validate_plugin_config(self, plugin_config: Dict[str, Any]) -> Dict[str, Any]:
        PluginConfigCls = DATA_SOURCE_PLUGIN_CONFIG_CLASS_MAP.get(self.context["plugin_id"])  # noqa: N806
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

        return field_mapping


class UserSearchInputSLZ(serializers.Serializer):
    username = serializers.CharField(required=False, help_text="用户名", allow_blank=True)


class DataSourceSearchDepartmentsOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="部门ID")
    name = serializers.CharField(help_text="部门名称")


class UserSearchOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户ID")
    username = serializers.CharField(help_text="用户名")
    full_name = serializers.CharField(help_text="全名")
    phone = serializers.CharField(help_text="手机号")
    email = serializers.CharField(help_text="邮箱")
    departments = serializers.SerializerMethodField(help_text="用户部门")

    # FIXME:考虑抽象一个函数 获取数据后传递到context
    @swagger_serializer_method(serializer_or_field=DataSourceSearchDepartmentsOutputSLZ(many=True))
    def get_departments(self, obj: DataSourceUser):
        return [
            {"id": department_user_relation.department.id, "name": department_user_relation.department.name}
            for department_user_relation in DataSourceDepartmentUserRelation.objects.filter(user=obj)
        ]


class UserCreateInputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="用户名", validators=[validate_data_source_user_username])
    full_name = serializers.CharField(help_text="姓名")
    email = serializers.EmailField(help_text="邮箱")
    phone_country_code = serializers.CharField(
        help_text="手机号国际区号", required=False, default=settings.DEFAULT_PHONE_COUNTRY_CODE
    )
    phone = serializers.CharField(help_text="手机号")
    logo = serializers.CharField(help_text="用户 Logo", required=False)
    department_ids = serializers.ListField(help_text="部门ID列表", child=serializers.IntegerField(), default=[])
    leader_ids = serializers.ListField(help_text="上级ID列表", child=serializers.IntegerField(), default=[])

    def validate(self, data):
        validate_phone_with_country_code(phone=data["phone"], country_code=data["phone_country_code"])
        return data

    def validate_department_ids(self, department_ids):
        diff_department_ids = set(department_ids) - set(
            DataSourceDepartment.objects.filter(
                id__in=department_ids, data_source=self.context["data_source"]
            ).values_list("id", flat=True)
        )
        if diff_department_ids:
            raise serializers.ValidationError(_("传递了错误的部门信息: {}").format(diff_department_ids))
        return department_ids

    def validate_leader_ids(self, leader_ids):
        diff_leader_ids = set(leader_ids) - set(
            DataSourceUser.objects.filter(id__in=leader_ids, data_source=self.context["data_source"]).values_list(
                "id", flat=True
            )
        )
        if diff_leader_ids:
            raise serializers.ValidationError(_("传递了错误的上级信息: {}").format(diff_leader_ids))
        return leader_ids


class UserCreateOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="数据源用户ID")


class LeaderSearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", required=False)


class LeaderSearchOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="上级ID")
    username = serializers.CharField(help_text="上级名称")


class DepartmentSearchInputSLZ(serializers.Serializer):
    name = serializers.CharField(required=False, help_text="部门名称", allow_blank=True)


class DepartmentSearchOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="部门ID")
    name = serializers.CharField(help_text="部门名称")
