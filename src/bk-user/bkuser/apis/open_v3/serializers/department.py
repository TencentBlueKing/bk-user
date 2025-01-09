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


class AncestorSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="祖先部门 ID")
    name = serializers.CharField(help_text="祖先部门名称")


class TenantDepartmentRetrieveInputSLZ(serializers.Serializer):
    with_ancestors = serializers.BooleanField(label="是否包括祖先部门", required=False, default=False)


class TenantDepartmentRetrieveOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="部门 ID")
    name = serializers.CharField(help_text="部门名称")
    ancestors = serializers.ListField(help_text="祖先部门列表", required=False, child=AncestorSLZ(), allow_empty=True)
