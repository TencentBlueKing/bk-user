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
import datetime

from django.db import models
from django.utils import timezone

from bkuser_core.common.models import TimestampedModel
from bkuser_core.recycle_bin.constants import RecycleBinObjectType
from bkuser_core.user_settings.constants import GlobalSettingsEnableNamespaces
from bkuser_core.user_settings.loader import GlobalConfigProvider


class RecycleBin(TimestampedModel):
    object_type = models.CharField("对象类型", choices=RecycleBinObjectType.get_choices(), max_length=64, default="")
    object_id = models.IntegerField("对象id")
    operator = models.CharField("操作人", max_length=255, default="")

    @property
    def expires(self) -> int:
        """
        过期剩余天数
        """
        config_loader = GlobalConfigProvider(namespace=GlobalSettingsEnableNamespaces.RECYCLING_STRATEGY.value)
        retention_days = config_loader["retention_days"]
        expire_at = self.create_time + datetime.timedelta(days=int(retention_days))
        return (expire_at - timezone.now()).days if expire_at > timezone.now() else 0

    def __str__(self):
        return f"{self.object_type}-{self.object_id}"

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "回收站信息"
        verbose_name_plural = "回收站信息"
        index_together = ("object_type", "object_id")
