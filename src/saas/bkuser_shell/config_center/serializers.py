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
from bkuser_sdk import DynamicFields
from rest_framework import serializers

from .constants import DynamicFieldTypeEnum


##########
# Fields #
##########
class ProfileTitlesSerializer(serializers.Serializer):
    key = serializers.CharField(source="name")
    name = serializers.CharField(source="display_name")


class ChoicesSerializer(serializers.Serializer):
    text = serializers.CharField()
    value = serializers.CharField()


class ProfileFieldsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    key = serializers.CharField(source="name")
    name = serializers.CharField(source="display_name")
    type = serializers.CharField()
    editable = serializers.BooleanField()
    configurable = serializers.BooleanField()
    builtin = serializers.BooleanField(required=False)
    unique = serializers.BooleanField()
    require = serializers.BooleanField()
    order = serializers.IntegerField()
    default = serializers.JSONField()
    options = serializers.SerializerMethodField(required=False)
    enabled = serializers.BooleanField(default=True, source="is_deleted")
    visible = serializers.BooleanField(default=True)

    def get_options(self, obj):
        if isinstance(obj, DynamicFields):
            if not obj.options:
                return []
            return [{"id": x[0], "value": x[1]} for x in obj.options]
        else:
            if not obj.get("options"):
                return []
            return [{"id": x[0], "value": x[1]} for x in obj["options"]]


class ProfileFieldsValueSerializer(ProfileFieldsSerializer):
    value = serializers.CharField(required=False)


class FieldsSaveSerializer(serializers.Serializer):
    name = serializers.CharField()
    display_name = serializers.CharField()
    builtin = serializers.BooleanField(required=False, default=False)
    require = serializers.BooleanField(required=False, default=False)
    unique = serializers.BooleanField(required=False, default=False)
    editable = serializers.BooleanField(required=False)
    options = serializers.JSONField()
    type = serializers.ChoiceField(choices=DynamicFieldTypeEnum.get_choices())
    default = serializers.JSONField(required=False)

    def to_internal_value(self, data):
        # 将前端存储转为后端格式
        if data.get("options"):
            data["options"] = [[x.get("id"), x.get("value")] for x in data["options"]]

        data["display_name"] = data.pop("name")
        data["name"] = data.pop("key")
        return data


class FieldsUpdateSerializer(serializers.Serializer):
    display_name = serializers.CharField(required=False)
    require = serializers.BooleanField(required=False, default=False)
    unique = serializers.BooleanField(required=False, default=False)
    options = serializers.JSONField(required=False)
    order = serializers.IntegerField(required=False)
    default = serializers.JSONField(required=False)

    def to_internal_value(self, data):
        if data.get("options"):
            data["options"] = [[x.get("id"), x.get("value")] for x in data["options"]]

        if data.get("name"):
            data["display_name"] = data.pop("name")

        return data


class ListFieldsSerializer(serializers.Serializer):
    only_visible = serializers.BooleanField(default=False)


class UpdateFieldsVisibleSerializer(serializers.Serializer):
    updating_ids = serializers.ListField(child=serializers.IntegerField())


############
# Settings #
############


class ListSettingsSerializer(serializers.Serializer):
    namespace = serializers.CharField(required=False)
    region = serializers.CharField(required=False)


class CreateSettingsSerializer(serializers.Serializer):
    namespace = serializers.CharField()
    region = serializers.CharField(required=False, default="default")
    key = serializers.CharField()
    value = serializers.JSONField()


class SettingSerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.JSONField()
    namespace = serializers.CharField(required=False)
    region = serializers.CharField()
    enabled = serializers.BooleanField(required=False, default=True)


class UpdateSettingSerializer(serializers.Serializer):
    value = serializers.JSONField(required=False)
    enabled = serializers.BooleanField(required=False)


#######################
# Settings  Namespace #
#######################


class ListNamespaceSettingsSerializer(serializers.Serializer):
    region = serializers.CharField(required=False, default="default")


class UpdateNamespaceSettingSerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.JSONField()


class SettingMetaSerializer(serializers.Serializer):
    key = serializers.CharField()
    example = serializers.JSONField()
    choices = serializers.JSONField()
    default = serializers.JSONField()
    namespace = serializers.CharField(required=False)
    region = serializers.CharField()
    enabled = serializers.BooleanField(required=False, default=True)


class ListSettingMetasSerializer(serializers.Serializer):
    category_type = serializers.CharField()
    namespace = serializers.CharField(required=False)
