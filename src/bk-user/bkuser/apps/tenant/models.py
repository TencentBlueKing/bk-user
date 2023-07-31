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
from django.utils.translation import gettext_lazy as _

from bkuser.apps.tenant.constants import TIME_ZONE_CHOICES, LanguageEnum


class Tenant(models.Model):
    id = models.CharField(primary_key=True, max_length=256, verbose_name=_("租户ID"))
    name = models.CharField(max_length=256, unique=True, verbose_name=_("租户名称"))
    logo = models.TextField(verbose_name=_("base64化的logo图片"), blank=True, null=True)
    is_default = models.BooleanField(default=False, verbose_name=_("默认租户"))
    enabled_user_count_display = models.BooleanField(default=False, verbose_name=_("使能可查看用户数量"))

    def __str__(self):
        return f"{self.id}-{self.name}"


class TenantDataSourceRelationShip(models.Model):
    tenant_id = models.CharField(max_length=256, verbose_name=_("逻辑外键：租户ID"))
    data_source_id = models.CharField(max_length=256, verbose_name=_("逻辑外键：数据源用户id"))

    class Meta:
        unique_together = ["tenant_id", "data_source_id"]


class TenantUser(models.Model):
    id = models.CharField(primary_key=True, max_length=64, verbose_name=_("租用用户ID/蓝鲸账户"))
    username = models.CharField(max_length=256, verbose_name=_("数据源username"))
    display_name = models.CharField(max_length=256, verbose_name=_("数据源display_name"))
    data_source_user_id = models.IntegerField(verbose_name=_("逻辑外键：数据源用户id"))
    tenant_id = models.CharField(max_length=256, verbose_name=_("逻辑外键：租户ID"))
    time_zone = models.CharField(
        verbose_name=_("时区"),
        choices=TIME_ZONE_CHOICES,
        default="Asia/Shanghai",
        max_length=32,
    )
    language = models.CharField(
        verbose_name=_("语言"),
        choices=LanguageEnum.get_choices(),
        default=LanguageEnum.ZH_CN.value,
        max_length=32,
    )

    def __str__(self):
        return f"{self.id}-{self.tenant_id}-{self.username}"


class TenantManager(models.Model):
    tenant_id = models.CharField(max_length=256, verbose_name="逻辑外键：租户ID")
    tenant_user_id = models.CharField(max_length=64, verbose_name="逻辑外键：租户用户ID")

    class Meta:
        unique_together = ("tenant_id", "tenant_user_id")
        index_together = ("tenant_id", "tenant_user_id")
