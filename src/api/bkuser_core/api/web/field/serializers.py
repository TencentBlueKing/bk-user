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

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import ValidationError

from bkuser_core.profiles.models import DynamicFieldInfo

# NOTE: 这里比较分裂的是, 前端输入的数据需要转换, 才能create/update, 并且吐出去之前要转成前端的格式


class FieldOutputSLZ(serializers.ModelSerializer):
    key = serializers.CharField(source="name")
    name = serializers.CharField(source="display_name")
    options = serializers.SerializerMethodField(required=False)

    def get_options(self, obj):
        if not obj.options:
            return []
        return [{"id": x[0], "value": x[1]} for x in obj.options]

    class Meta:
        model = DynamicFieldInfo
        exclude = (
            # NOTE: category export profile need the display_name => CategoryOperationExportApi
            # "display_name",
            "display_name_en",
            "display_name_zh_hans",
            "map_method",
            "update_time",
            "create_time",
        )


class DynamicFieldUpdateVisibleInputSLZ(serializers.Serializer):
    updating_ids = serializers.ListField(child=serializers.IntegerField())


class DynamicFieldCreateInputSLZ(serializers.ModelSerializer):
    class Meta:
        model = DynamicFieldInfo
        fields = ["name", "display_name", "builtin", "require", "unique", "options", "type", "default"]

    def to_internal_value(self, data):
        # 将前端存储转为后端格式
        if data.get("options"):
            data["options"] = [[x.get("id"), x.get("value")] for x in data["options"]]

        data["display_name"] = data.pop("name")
        data["name"] = data.pop("key")
        return data

    def validate(self, attrs):
        if DynamicFieldInfo.objects.filter(name=attrs["name"]).exists():
            raise ValidationError(_("英文标识为 {} 的自定义字段已存在").format(attrs["name"]))

        return super().validate(attrs)


class DynamicFieldUpdateInputSLZ(serializers.Serializer):
    name = serializers.CharField(required=False)
    require = serializers.BooleanField(required=False, default=False)
    unique = serializers.BooleanField(required=False, default=False)
    editable = serializers.BooleanField(required=False, default=False)
    options = serializers.JSONField(required=False)
    order = serializers.IntegerField(required=False)
    default = serializers.JSONField(required=False)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if data.get("options"):
            data["options"] = [[x.get("id"), x.get("value")] for x in data["options"]]

        if data.get("name"):
            data["display_name"] = data.pop("name")

        return data
