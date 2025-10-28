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

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from bkuser.apps.audit.constants import ObjectTypeEnum, OperationEnum


class AuditRecordListInputSLZ(serializers.Serializer):
    operation = serializers.ChoiceField(help_text="操作行为", choices=OperationEnum.get_choices(), required=False)
    object_type = serializers.ChoiceField(
        help_text="操作对象类型", choices=ObjectTypeEnum.get_choices(), required=False
    )
    object_name = serializers.CharField(help_text="操作对象名称", required=False, allow_blank=True)
    creator = serializers.CharField(help_text="操作人", required=False, allow_blank=True)
    start_at = serializers.DateTimeField(help_text="开始时间", required=False)
    end_at = serializers.DateTimeField(help_text="结束时间", required=False)

    def validate(self, attrs):
        start_at = attrs.get("start_at")
        end_at = attrs.get("end_at")

        if (start_at and not end_at) or (not start_at and end_at):
            raise serializers.ValidationError(_("开始时间和结束时间参数不能仅提供其中一个"))

        if start_at and end_at and start_at > end_at:
            raise serializers.ValidationError(_("开始时间不能大于结束时间"))

        return attrs


class AuditRecordListOutputSLZ(serializers.Serializer):
    operation = serializers.CharField(help_text="操作行为")
    object_type = serializers.CharField(help_text="操作对象类型")
    object_name = serializers.CharField(help_text="操作对象名称", allow_blank=True, allow_null=True)
    creator = serializers.CharField(help_text="操作人")
    created_at = serializers.DateTimeField(help_text="操作时间")
