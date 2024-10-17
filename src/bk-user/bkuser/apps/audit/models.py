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

import uuid

from django.db import models

from bkuser.common.models import AuditedModel


class OperationAuditRecord(AuditedModel):
    id = models.UUIDField(
        "事件 id", default=uuid.uuid4, primary_key=True, editable=False, auto_created=True, unique=True
    )
    operation_target = models.CharField(max_length=32, verbose_name="操作对象")
    operation_type = models.CharField(max_length=32, verbose_name="操作类型")
    tenant_id = models.CharField(max_length=32, verbose_name="操作对象所属的租户 id")
    data_change = models.JSONField(max_length=32, verbose_name="操作数据变更", null=True, blank=True)
    data_source_id = models.CharField(max_length=32, verbose_name="操作对象所属的数据源 id", null=True, blank=True)
    extras = models.JSONField(verbose_name="操作额外信息", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]  # 按照 created_at 字段降序排列
