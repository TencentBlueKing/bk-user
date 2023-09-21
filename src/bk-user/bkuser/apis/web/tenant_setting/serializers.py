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

from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from bkuser.apps.tenant_setting.constants import UserFieldDataType
from bkuser.apps.tenant_setting.models import UserCustomField

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


class CustomFieldOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="字段ID", read_only=True)
    name = serializers.CharField(help_text="字段名称")
    display_name = serializers.CharField(help_text="展示用名称")
    data_type = serializers.CharField(help_text="字段类型")
    required = serializers.BooleanField(help_text="是否必填")
    default = serializers.JSONField(help_text="默认值")
    options = serializers.JSONField(help_text="选项")


class UserFieldOutputSLZ(serializers.Serializer):
    builtin_fields = serializers.SerializerMethodField(help_text="内置字段")
    custom_fields = serializers.SerializerMethodField(help_text="自定义字段")

    @swagger_serializer_method(serializer_or_field=BuiltinFieldOutputSLZ(many=True))
    def get_builtin_fields(self, obj):
        return BuiltinFieldOutputSLZ(obj["builtin_fields"], many=True).data

    @swagger_serializer_method(serializer_or_field=CustomFieldOutputSLZ(many=True))
    def get_custom_fields(self, obj):
        return CustomFieldOutputSLZ(obj["custom_fields"], many=True).data


class UserCustomFieldCreateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="字段名称", max_length=128)
    display_name = serializers.CharField(help_text="展示用名称", max_length=128)
    data_type = serializers.ChoiceField(help_text="字段类型", choices=UserFieldDataType.get_choices())
    required = serializers.BooleanField(help_text="是否必填")
    default = serializers.JSONField(help_text="默认值", required=False)
    options = serializers.JSONField(help_text="选项", required=False)

    def validate_display_name(self, display_name):
        if UserCustomField.objects.filter(tenant=self.context["tenant"], display_name=display_name).exists():
            raise serializers.ValidationError("display_name already exists")
        return display_name

    def validate_name(self, name):
        if UserCustomField.objects.filter(tenant=self.context["tenant"], name=name).exists():
            raise serializers.ValidationError("name already exists")
        return name

    def validate(self, data):
        data_type = data.get("data_type")
        default = data.get("default")
        options = data.get("options")

        if data_type in [UserFieldDataType.ENUM.value, UserFieldDataType.MULTI_ENUM.value] and (
            default is None or options is None
        ):
            raise serializers.ValidationError(
                "default and options fields are required for enum and multi_enum data types"
            )

        return data


class UserCustomFieldCreateOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField()


class UserCustomFieldUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(help_text="字段名称", max_length=128, required=False)
    required = serializers.BooleanField(help_text="是否必填", required=False)
    default = serializers.JSONField(help_text="默认值", required=False)
    options = serializers.JSONField(help_text="选项", required=False)
