# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.db import models

from bkuser.common.time import datetime_to_display


class TimestampedModel(models.Model):
    """Model with 'created' and 'updated' fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def created_at_display(self):
        # 转换成本地时间
        return datetime_to_display(self.created_at)

    @property
    def updated_at_display(self):
        # 转换成本地时间
        return datetime_to_display(self.updated_at)

    class Meta:
        abstract = True


class AuditedModel(TimestampedModel):
    """Model with 'created', 'updated', 'creator' and 'updater' fields."""

    creator = models.CharField(max_length=128, null=True, blank=True)
    updater = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        abstract = True
