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
from django.utils import timezone


class TimestampedModel(models.Model):
    """Model with 'created' and 'updated' fields."""

    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    @property
    def created_time_display(self):
        # 转换成本地时间
        local_time = timezone.localtime(self.created_time)
        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def updated_time_display(self):
        # 转换成本地时间
        local_time = timezone.localtime(self.updated_time)
        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        abstract = True
