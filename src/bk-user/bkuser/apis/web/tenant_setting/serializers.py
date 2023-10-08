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
from typing import List, Dict

from django.utils.translation import gettext_lazy as _
from pydantic import ValidationError as PDValidationError
from rest_framework import serializers

from bkuser.apps.tenant.models import TenantUserCustomField
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.data_models import TenantUserCustomFieldOptions

logger = logging.getLogger(__name__)


class BuiltinFieldOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="字段ID", read_only=True)
    name = serializers.CharField(help_text="字段名称")
    display_name = serializers.CharField(help_text="展示用名称")
    data_type = serializers.CharField(help_text="字段类型")
    required = serializers.BooleanField(help_text="是否必填")
    unique = serializers.BooleanField(help_text="是否唯一")
    default = serializers.JSONField(help_text="默认值")
    options = serializers.JSONField(help_text="选项")


class TenantUserCustomFieldOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="字段ID", read_only=True)
    name = serializers.CharField(help_text="字段名称")
    display_name = serializers.CharField(help_text="展示用名称")
    data_type = serializers.CharField(help_text="字段类型")
    required = serializers.BooleanField(help_text="是否必填")
    default = serializers.JSONField(help_text="默认值")
    options = serializers.JSONField(help_text="选项")


class TenantUserFieldOutputSLZ(serializers.Serializer):
    builtin_fields = serializers.ListField(help_text="内置字段", child=BuiltinFieldOutputSLZ())
    custom_fields = serializers.ListField(help_text="自定义字段", child=TenantUserCustomFieldOutputSLZ())


class TenantUserCustomFieldCreateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="字段名称", max_length=128)
    display_name = serializers.CharField(help_text="展示用名称", max_length=128)
    data_type = serializers.ChoiceField(help_text="字段类型", choices=UserFieldDataType.get_choices())
    required = serializers.BooleanField(help_text="是否必填")
    default = serializers.JSONField(help_text="默认值", required=False)
    options = serializers.JSONField(help_text="选项", required=False)

    def validate_display_name(self, display_name):
        if TenantUserCustomField.objects.filter(
            tenant_id=self.context["tenant_id"], display_name=display_name
        ).exists():
            raise serializers.ValidationError(_("展示用名称 {} 已存在").format(display_name))
        return display_name

    def validate_name(self, name):
        if TenantUserCustomField.objects.filter(tenant_id=self.context["tenant_id"], name=name).exists():
            raise serializers.ValidationError(_("字段名称 {} 已存在").format(name))
        return name

    def validate(self, attrs):
        data_type = attrs.get("data_type")
        options = attrs.get("options")
        default = attrs.get("default")

        if data_type == UserFieldDataType.ENUM.value:
            self._validate_options(options)
            self._validate_enum_default(default, options)

        elif data_type == UserFieldDataType.MULTI_ENUM.value:
            self._validate_options(options)
            self._validate_multi_enum_default(default, options)

        return attrs

    def _validate_options(self, options):
        if not options:
            raise serializers.ValidationError(_("枚举类型的自定义字段需要传递非空的<选项>字段"))
        try:
            TenantUserCustomFieldOptions(options=options)
        except PDValidationError as e:
            raise serializers.ValidationError(_("<选项>字段不合法: {}".format(e)))

    def _validate_enum_default(self, default: int, options: List[Dict]):
        if not isinstance(default, int):
            raise TypeError("枚举类型自定义字段的 default 值要传递整数类型")

        # 单枚举类型要求 default 的值为 options 其中一个对象的 ID 值
        if not (default or default in [opt["id"] for opt in options]):
            raise serializers.ValidationError(_("默认值必须是 options 中对象的其中一个 id 值"))

    def _validate_multi_enum_default(self, default: List[int], options: List[Dict]):
        if not isinstance(default, List):
            raise TypeError("多选枚举类型自定义字段的 default 值需要传递列表类型")

        # 多选枚举类型要求 default 中的值都为 options 其中任一对象的 ID 值
        if not (default or set(default).issubset({opt["id"] for opt in options})):
            raise serializers.ValidationError(_("默认值必须属于 options 中对象的 id 值"))


class TenantUserCustomFieldCreateOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField()


class TenantUserCustomFieldUpdateInputSLZ(serializers.Serializer):
    display_name = serializers.CharField(help_text="展示用名称", max_length=128)
    required = serializers.BooleanField(help_text="是否必填")
    default = serializers.JSONField(help_text="默认值")
    options = serializers.JSONField(help_text="选项")

    def validate_display_name(self, display_name):
        if (
            TenantUserCustomField.objects.filter(tenant_id=self.context["tenant_id"], display_name=display_name)
            .exclude(id=self.context["current_custom_field_id"])
            .exists()
        ):
            raise serializers.ValidationError(_("展示用名称 {} 已存在").format(display_name))
        return display_name

    def validate(self, attrs):
        current_custom_field = TenantUserCustomField.objects.get(id=self.context["current_custom_field_id"])
        data_type = current_custom_field.data_type
        options = attrs.get("options")
        default = attrs.get("default")

        if data_type == UserFieldDataType.ENUM.value:
            self._validate_options(options=options)
            self._validate_enum_default(default=default, options=options)

        elif data_type == UserFieldDataType.MULTI_ENUM.value:
            self._validate_options(options=options)
            self._validate_multi_enum_default(default=default, options=options)

        return attrs

    def _validate_options(self, options):
        if not options:
            raise serializers.ValidationError(_("枚举类型的自定义字段需要传递非空的<选项>字段"))
        try:
            TenantUserCustomFieldOptions(options=options)
        except PDValidationError as e:
            raise serializers.ValidationError(_("<选项>字段不合法: {}".format(e)))

    def _validate_enum_default(self, default: int, options: List[Dict]):
        if not isinstance(default, int):
            raise TypeError("枚举类型自定义字段的 default 值要传递整数类型")

        # 单枚举类型要求 default 的值为 options 其中一个对象的 ID 值
        if not (default or default in [opt["id"] for opt in options]):
            raise serializers.ValidationError(_("默认值必须是 options 中对象的其中一个 id 值"))

    def _validate_multi_enum_default(self, default: List[int], options: List[Dict]):
        if not isinstance(default, List):
            raise TypeError("多选枚举类型自定义字段的 default 值需要传递列表类型")

        # 多选枚举类型要求 default 中的值都为 options 其中任一对象的 ID 值
        if not (default or set(default).issubset({opt["id"] for opt in options})):
            raise serializers.ValidationError(_("默认值必须属于 options 中对象的 id 值"))
