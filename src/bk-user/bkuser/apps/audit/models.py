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

from django.db import models

from bkuser.common.models import AuditedModel
from bkuser.utils.uuid import generate_uuid


class OperationAuditRecord(AuditedModel):
    """
    SaaS 审计操作记录
    """

    id = models.CharField(primary_key=True, max_length=128, default=generate_uuid)
    # 若操作记录具有相同的事件 ID，则表示这些记录由同一个事件触发，特别是批量操作
    event_id = models.CharField("事件 ID", max_length=128, default=generate_uuid)
    # 操作对象所属的租户 ID
    tenant_id = models.CharField("租户 ID", max_length=128)

    # ----------------------- 操作相关 -----------------------
    operation = models.CharField("操作行为", max_length=64)
    object_type = models.CharField("操作对象类型", max_length=32)
    object_id = models.CharField("操作对象 ID", max_length=128)
    # 与操作对象相关的额外信息，有助于问题溯源
    extras = models.JSONField("额外信息", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]  # 按照 created_at 字段降序排列
