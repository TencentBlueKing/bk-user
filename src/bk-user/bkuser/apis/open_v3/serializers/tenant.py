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
from typing import List

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.tenant.constants import TenantStatus
from bkuser.common.serializers import StringArrayField


class TenantListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名")
    status = serializers.ChoiceField(help_text="租户状态", choices=TenantStatus.get_choices())


class TenantPropertyListOutputSLZ(serializers.Serializer):
    key = serializers.CharField(help_text="租户公共属性名")
    value = serializers.CharField(help_text="租户公共属性值")


class TenantPropertyLookupInputSLZ(serializers.Serializer):
    lookups = StringArrayField(help_text="租户公共属性名, 多个使用逗号分隔", max_items=100)

    def validate_lookups(self, lookups: List[str]) -> List[str]:
        max_length = 255
        if invalid_lookups := [i for i in lookups if len(i) > max_length]:
            raise ValidationError(
                "The length of the specified lookup value {} exceeds the 255-character limit.".format(
                    ", ".join(invalid_lookups)
                )
            )
        return lookups


class TenantPropertyLookupOutputSLZ(serializers.Serializer):
    key = serializers.CharField(help_text="租户公共属性名")
    value = serializers.CharField(help_text="租户公共属性值")
