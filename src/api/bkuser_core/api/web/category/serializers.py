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
from typing import List

from rest_framework import serializers

from bkuser_core.bkiam.serializers import AuthInfoSLZ
from bkuser_core.categories.constants import CategoryStatus
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.user_settings.models import Setting


class ExtraInfoSerializer(serializers.Serializer):
    auth_infos = serializers.ListField(read_only=True, child=AuthInfoSLZ())
    callback_url = serializers.CharField(read_only=True)


class CategoryMetaSerializer(serializers.Serializer):
    """用户目录基本信息"""

    type = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    authorized = serializers.BooleanField(read_only=True, default=True)
    extra_info = ExtraInfoSerializer(read_only=True, default={})


class CategorySettingListSerializer(serializers.Serializer):
    namespace = serializers.CharField(required=False)
    region = serializers.CharField(required=False)


class CategorySettingSerializer(serializers.ModelSerializer):
    """配置项"""

    # NOTE: 这里只包含这几个字段的原因是, 目前只有category settings拿, 没有其他地方用到
    # 其他地方用到, 可以实现更通用的 slz

    key = serializers.CharField(source="meta.key", required=False)
    namespace = serializers.CharField(source="meta.namespace", required=False)
    region = serializers.CharField(source="meta.region", required=False)
    value = serializers.JSONField()

    class Meta:
        model = Setting
        fields = ["key", "namespace", "region", "value", "enabled"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    configured = serializers.SerializerMethodField()
    unfilled_namespaces = serializers.SerializerMethodField(required=False)
    activated = serializers.SerializerMethodField()

    def get_configured(self, obj) -> bool:
        return obj.configured

    def get_unfilled_namespaces(self, obj) -> List[str]:
        unfilled_nss = set(obj.get_unfilled_settings().values_list("namespace", flat=True))
        return list(unfilled_nss)

    def get_activated(self, obj) -> bool:
        return obj.status == CategoryStatus.NORMAL.value

    class Meta:
        model = ProfileCategory
        fields = "__all__"


class CategoryUpdateSerializer(serializers.Serializer):
    display_name = serializers.CharField(max_length=64, required=False)
    activated = serializers.BooleanField(default=True, required=False)
    description = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        # NOTE: 这里做了activated的转换, 所以需要自定义update => 能否整合model serializer复用原先的方法, 只需要处理activated
        has_changed = False
        activated = validated_data.get("activated", None)
        if activated is not None:
            has_changed = True
            instance.status = CategoryStatus.NORMAL.value if activated else CategoryStatus.INACTIVE.value

        display_name = validated_data.get("display_name")
        if display_name:
            has_changed = True
            instance.display_name = display_name

        description = validated_data.get("description")
        if description:
            has_changed = True
            instance.description = description

        if has_changed:
            instance.save()
        return instance


class CategoryTestConnectionSerializer(serializers.Serializer):
    connection_url = serializers.CharField()
    user = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    timeout_setting = serializers.IntegerField(required=False, default=120)
    use_ssl = serializers.BooleanField(default=False, required=False)


class CategoryTestFetchDataSerializer(serializers.Serializer):
    basic_pull_node = serializers.CharField()
    user_filter = serializers.CharField()
    organization_class = serializers.CharField()
    user_group_filter = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    user_member_of = serializers.CharField(required=False, allow_blank=True, allow_null=True)
