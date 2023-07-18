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
from bkuser.common.models import TimestampedModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class Tenant(TimestampedModel):
    id = models.CharField(primary_key=True, max_length=256)
    name = models.CharField(max_length=256, unique=True, verbose_name=_("租户名称"))
    logo = models.TextField(verbose_name=_("base64化的logo图片"), blank=True, null=True)
    is_default = models.BooleanField(default=False, verbose_name=_("默认租户"))
    enabled_user_count_display = models.BooleanField(default=False, verbose_name=_("使能可查看用户数量"))

    def __str__(self):
        return f"{self.id}-{self.name}"


class TenantUser(TimestampedModel):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=256, verbose_name=_("数据源username"))
    display_name = models.CharField(max_length=256)
    logo = models.TextField(max_length=256)
    is_default = models.BooleanField(default=False)
    data_source_user_id = models.IntegerField(verbose_name=_("逻辑外键：数据源用户id"))
    tenant_id = models.CharField(max_length=256, verbose_name=_("逻辑外键：租户ID"))

    def __str__(self):
        return f"{self.id}-{self.tenant_id}-{self.username}"


class TenantManager(TimestampedModel):
    id = models.CharField(primary_key=True, max_length=256)
    tenant_user_id = models.CharField(max_length=256)
    # tenant_id = models.UUIDField(max_length=256)
    tenant_id = models.IntegerField()


class TenantDataSourceBinding(TimestampedModel):
    id = models.IntegerField(primary_key=True)
    tenant_id = models.IntegerField()
    data_source_id = models.CharField(max_length=256)


class DataSource(TimestampedModel):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=256, verbose_name=_("数据源名称"))
    code = models.CharField(max_length=256)
    status = models.CharField(max_length=256)


# 租户下用户的邮箱和手机号从这里获取
class DataSourceUser(TimestampedModel):
    id = models.IntegerField(primary_key=True)
    data_source_id = models.CharField(max_length=256)
    username = models.CharField(verbose_name=_("用户名"), max_length=255)
    display_name = models.CharField(max_length=256)
    email = models.EmailField(verbose_name=_("邮箱"), null=True, blank=True, default="", max_length=255)
    telephone = models.CharField(verbose_name=_("手机号码"), null=True, blank=True, default="", max_length=255)
    logo = models.TextField(max_length=256)
    staff_status = models.CharField(max_length=256)
    is_deleted = models.BooleanField(default=False)
