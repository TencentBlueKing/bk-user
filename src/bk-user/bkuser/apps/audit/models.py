# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.db import models

from bkuser.common.models import AuditedModel
from bkuser.utils.uuid import generate_uuid


class OperationAuditRecord(AuditedModel):
    id = models.CharField(primary_key=True, max_length=128, default=generate_uuid)
    event_id = models.CharField(max_length=128, default=generate_uuid, verbose_name="事件 ID")
    operation = models.CharField(max_length=64, verbose_name="操作行为")
    object_type = models.CharField(max_length=32, verbose_name="操作对象类型")
    object_id = models.CharField(max_length=128, verbose_name="操作对象 ID")
    tenant_id = models.CharField(max_length=128, verbose_name="租户 ID")
    extras = models.JSONField(verbose_name="额外信息", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]  # 按照 created_at 字段降序排列
