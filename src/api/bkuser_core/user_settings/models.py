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
import jsonfield
from django.db import models

from .constants import GlobalSettingsEnableNamespaces, SettingsEnableNamespaces
from .managers import SettingManager, SettingMetaManager
from bkuser_core.audit.models import AuditObjMetaInfo
from bkuser_core.categories.constants import CategoryType
from bkuser_core.common.models import TimestampedModel


class Setting(TimestampedModel):
    """配置项"""

    value = jsonfield.JSONField("配置内容", default={})
    enabled = models.BooleanField(default=True)

    meta = models.ForeignKey("user_settings.SettingMeta", related_name="instances", on_delete=models.CASCADE)
    # null 表示为全局配置
    category = models.ForeignKey(
        "categories.ProfileCategory",
        related_name="settings",
        null=True,
        on_delete=models.CASCADE,
    )

    objects = SettingManager()

    class Meta:
        verbose_name = "配置表"
        verbose_name_plural = "配置表"
        ordering = ["-create_time"]
        unique_together = ["category", "meta"]

    def __str__(self):
        return f"{self.meta.namespace}-{self.meta.region}-{self.meta.key}"

    def to_audit_info(self):
        """提供审计元信息"""
        return AuditObjMetaInfo(
            key=self.meta.key,
            display_name=f"{self.meta.key}",
            category_id=self.category.id,
        )


class SettingMeta(TimestampedModel):
    """配置项元信息"""

    key = models.CharField("配置键", max_length=64)
    enabled = models.BooleanField(default=True)
    example = jsonfield.JSONField("示例", default="")
    default = jsonfield.JSONField("默认值", default=None)
    choices = jsonfield.JSONField("可选值", default=[])
    required = models.BooleanField("是否必要", default=False)
    namespace = models.CharField(
        "命名空间",
        max_length=32,
        db_index=True,
        choices=SettingsEnableNamespaces.get_choices(),
        default=SettingsEnableNamespaces.GENERAL.value,
    )
    # 对配置项的更细分
    region = models.CharField("领域", max_length=32, default="default")
    category_type = models.CharField(verbose_name="类型", max_length=32, choices=CategoryType.get_choices())

    objects = SettingMetaManager()

    def __str__(self):
        return f"{self.key}-{self.namespace}-{self.category_type}"

    class Meta:
        verbose_name = "配置元信息表"
        verbose_name_plural = "配置元信息表"
        unique_together = ("key", "namespace", "category_type")
        ordering = ["-create_time"]


class GlobalSettings(TimestampedModel):

    key = models.CharField("配置键", max_length=64)
    value = jsonfield.JSONField("配置内容", default={})
    enabled = models.BooleanField(default=True)
    default = jsonfield.JSONField("默认值", default=None)
    choices = jsonfield.JSONField("可选值", default=[])
    namespace = models.CharField(
        "命名空间",
        max_length=32,
        db_index=True,
        choices=GlobalSettingsEnableNamespaces.get_choices(),
        default=GlobalSettingsEnableNamespaces.GENERAL.value,
    )
    # 对配置项的更细分
    region = models.CharField("领域", max_length=32, default="default")

    def __str__(self):
        return f"{self.namespace}-{self.key}"

    class Meta:
        verbose_name = "全局配置信息表"
        verbose_name_plural = "全局配置信息表"
        unique_together = ("key", "namespace")
        ordering = ["-create_time"]
        db_table = "global_settings"
