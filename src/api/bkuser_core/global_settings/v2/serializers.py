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

from bkuser_core.apis.v2.serializers import CustomFieldsModelSerializer
from bkuser_core.global_settings.models import GlobalSettings, GlobalSettingsMeta


class GlobalSettingsSerializer(CustomFieldsModelSerializer):
    """配置项"""

    key = serializers.CharField(required=False)
    namespace = serializers.CharField(required=False)
    region = serializers.CharField(required=False)
    value = serializers.JSONField()

    def to_representation(self, instance):
        data = super().to_representation(instance)

        for meta_field in ["key", "namespace", "region"]:
            data[meta_field] = getattr(instance.meta, meta_field)

        return data

    class Meta:
        model = GlobalSettings
        fields = "__all__"


class GlobalSettingsListSerializer(serializers.Serializer):
    key = serializers.CharField(required=False)
    namespace = serializers.CharField(required=False)
    region = serializers.CharField(required=False)
    enabled = serializers.BooleanField(required=True)


class GlobalSettingsUpdateSerializer(serializers.Serializer):
    value = serializers.JSONField()
    enabled = serializers.BooleanField(default=True)


class GlobalSettingsMetaSerializer(CustomFieldsModelSerializer):
    """配置信息项"""

    choices = serializers.JSONField()
    example = serializers.JSONField()
    default = serializers.JSONField()

    class Meta:
        model = GlobalSettingsMeta
        fields = "__all__"
