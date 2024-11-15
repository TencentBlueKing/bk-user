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

from bkuser.apps.audit.constants import ObjectTypeEnum, OperationEnum
from bkuser.apps.audit.models import OperationAuditRecord


class AuditRecordListInputSLZ(serializers.Serializer):
    creator = serializers.CharField(help_text="操作人", required=False, allow_blank=True)
    operation = serializers.ChoiceField(help_text="操作行为", choices=OperationEnum.get_choices(), required=False)
    object_type = serializers.ChoiceField(
        help_text="操作对象类型", choices=ObjectTypeEnum.get_choices(), required=False
    )
    object_name = serializers.CharField(help_text="操作对象名称", required=False, allow_blank=True)
    created_at = serializers.DateTimeField(help_text="操作时间", required=False)


class AuditRecordListOutputSLZ(serializers.Serializer):
    creator = serializers.SerializerMethodField(help_text="操作人")
    operation = serializers.CharField(help_text="操作行为")
    object_type = serializers.CharField(help_text="操作对象类型")
    object_name = serializers.CharField(help_text="操作对象名称", allow_blank=True, allow_null=True)
    created_at = serializers.DateTimeField(help_text="操作时间")

    def get_creator(self, obj: OperationAuditRecord) -> str:
        return self.context["user_display_name_map"].get(obj.creator) or obj.creator
