# -*- coding: utf-8 -*-
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
