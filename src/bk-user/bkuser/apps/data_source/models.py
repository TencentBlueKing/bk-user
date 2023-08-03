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

from bkuser.common.models import TimestampedModel


class DataSourcePlugin(models.Model):
    """
    数据源插件
    DB初始化内置插件：local/mad/ldap
    """

    id = models.CharField("数据源插件唯一标识", primary_key=True, max_length=128)
    name = models.CharField("数据源插件名称", max_length=128, unique=True)
    description = models.TextField("描述", default="", blank=True)
    logo = models.TextField("Logo", null=True, blank=True, default="")


class DataSource(TimestampedModel):
    name = models.CharField("数据源名称", max_length=128, unique=True)
    owner_tenant_id = models.CharField("归属租户", max_length=64, db_index=True)
    # Note: 数据源插件被删除的前提是，插件没有被任何数据源使用
    plugin = models.ForeignKey(DataSourcePlugin, on_delete=models.PROTECT)
    plugin_config = models.JSONField("数据源插件配置", default=dict)
    # 同步任务启用/禁用配置、周期配置等
    sync_config = models.JSONField("数据源同步任务配置", default=dict)
    # 字段映射，外部数据源提供商，用户数据字段映射到租户用户数据字段
    field_mapping = models.JSONField("用户字段映射", default=dict)

    class Meta:
        ordering = ["id"]
