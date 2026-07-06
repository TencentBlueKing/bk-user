# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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

from bkuser.apis.open_provider.constants import PROVIDER_BATCH_SIZE


class DepartmentCreateItemSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="部门唯一标识（数据源内）", max_length=128)
    name = serializers.CharField(help_text="部门名称", max_length=255)


class DepartmentBatchCreateInputSLZ(serializers.Serializer):
    departments = serializers.ListField(
        help_text="部门列表",
        child=DepartmentCreateItemSLZ(),
        min_length=1,
        max_length=PROVIDER_BATCH_SIZE,
    )


class DepartmentUpdateItemSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="部门唯一标识（数据源内）", max_length=128)
    name = serializers.CharField(help_text="部门名称", max_length=255)


class DepartmentBatchUpdateInputSLZ(serializers.Serializer):
    departments = serializers.ListField(
        help_text="部门列表",
        child=DepartmentUpdateItemSLZ(),
        min_length=1,
        max_length=PROVIDER_BATCH_SIZE,
    )


class DepartmentBatchDeleteInputSLZ(serializers.Serializer):
    ids = serializers.ListField(
        help_text="部门唯一标识列表",
        child=serializers.CharField(),
        min_length=1,
        max_length=PROVIDER_BATCH_SIZE,
    )
