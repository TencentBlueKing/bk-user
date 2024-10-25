# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from rest_framework import serializers


class CategoriesListInputSLZ(serializers.Serializer):
    no_page = serializers.BooleanField(help_text="全量返回", default=False)


class CategoriesListOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="目录 ID")
    display_name = serializers.CharField(help_text="目录名称")
    type = serializers.CharField(help_text="目录类型", default="")
    description = serializers.CharField(help_text="目录描述", default="")
    domain = serializers.CharField(help_text="所属租户域名")
    default = serializers.BooleanField(help_text="是否为默认目录")
    status = serializers.CharField(help_text="目录状态")
    enabled = serializers.BooleanField(help_text="是否启用")
