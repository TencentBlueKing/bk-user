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

from bkuser_core.bkiam.serializers import AuthInfoSLZ
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
