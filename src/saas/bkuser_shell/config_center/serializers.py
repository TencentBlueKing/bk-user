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
from rest_framework import serializers

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
    enabled = serializers.BooleanField(required=False, default=True)


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
