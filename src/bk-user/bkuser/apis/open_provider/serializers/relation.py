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

# ============== 部门父子关系 ==============


class DepartmentRelationItemSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="部门唯一标识（数据源内）", max_length=128)
    parent = serializers.CharField(
        help_text="父部门唯一标识，null 表示设为根部门",
        allow_null=True,
        max_length=128,
    )


class DepartmentRelationBatchInputSLZ(serializers.Serializer):
    relations = serializers.ListField(
        help_text="部门关系列表",
        child=DepartmentRelationItemSLZ(),
        min_length=1,
        max_length=PROVIDER_BATCH_SIZE,
    )


# ============== 用户-部门关系 ==============


class DepartmentUserRelationItemSLZ(serializers.Serializer):
    user_id = serializers.CharField(help_text="用户唯一标识（数据源内）", max_length=128)
    department_id = serializers.CharField(help_text="部门唯一标识（数据源内）", max_length=128)


class DepartmentUserRelationBatchCreateInputSLZ(serializers.Serializer):
    relations = serializers.ListField(
        help_text="用户-部门关系列表",
        child=DepartmentUserRelationItemSLZ(),
        min_length=1,
        max_length=PROVIDER_BATCH_SIZE,
    )


class DepartmentUserRelationBatchDeleteInputSLZ(serializers.Serializer):
    relations = serializers.ListField(
        help_text="用户-部门关系列表",
        child=DepartmentUserRelationItemSLZ(),
        min_length=1,
        max_length=PROVIDER_BATCH_SIZE,
    )


# ============== 用户-Leader 关系 ==============


class UserLeaderRelationItemSLZ(serializers.Serializer):
    user_id = serializers.CharField(help_text="用户唯一标识（数据源内）", max_length=128)
    leader_ids = serializers.ListField(
        help_text="Leader 用户唯一标识列表",
        child=serializers.CharField(),
        min_length=1,
    )


class UserLeaderRelationBatchCreateInputSLZ(serializers.Serializer):
    relations = serializers.ListField(
        help_text="用户-Leader 关系列表",
        child=UserLeaderRelationItemSLZ(),
        min_length=1,
        max_length=PROVIDER_BATCH_SIZE,
    )


class UserLeaderRelationBatchDeleteInputSLZ(serializers.Serializer):
    relations = serializers.ListField(
        help_text="用户-Leader 关系列表",
        child=UserLeaderRelationItemSLZ(),
        min_length=1,
        max_length=PROVIDER_BATCH_SIZE,
    )
