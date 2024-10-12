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

from bkuser.apps.audit.constants import OperationEnum, OperationTarget


class OperationAuditRecord(models.Model):
    event_id = models.UUIDField(
        "事件 id", default=uuid.uuid4, primary_key=True, editable=False, auto_created=True, unique=True
    )
    operator = models.CharField(max_length=32, verbose_name="操作用户")
    ip = models.CharField(max_length=32, verbose_name="来源 ip", null=True, blank=True)
    operate_time = models.DateTimeField(auto_now_add=True, verbose_name="操作时间", db_index=True)
    target = models.CharField(max_length=32, verbose_name="操作对象", choices=OperationTarget.get_choices())
    operation = models.CharField(max_length=32, verbose_name="操作类型", choices=OperationEnum.get_choices())
    data_before = models.JSONField(verbose_name="操作前的数据", null=True, blank=True)
    data_after = models.JSONField(verbose_name="操作后的数据", null=True, blank=True)
    instance = models.JSONField(verbose_name="操作对象实例", null=True, blank=True)

    class Meta:
        ordering = ["-operate_time"]  # 按照 operate_time 字段降序排列
