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


class SearchSerializer(serializers.Serializer):
    keyword = serializers.CharField()
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=10)
    no_page = serializers.BooleanField(default=False)
    max_items = serializers.IntegerField(required=False, default=20)


class SearchResultSerializer(serializers.Serializer):
    type = serializers.CharField()
    display_name = serializers.CharField()
    items = serializers.ListField(help_text="Profile 或 Department 对象列表，请直接参考模型定义")
