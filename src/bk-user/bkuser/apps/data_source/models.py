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


class DataSourcePlugin(models.Model):
    type = models.CharField(max_length=256, verbose_name=_("数据源插件类型"))
    name = models.CharField(max_length=256, verbose_name=_("数据源插件名称"))
    config_meta = models.JSONField(verbose_name=_("数据源插件源配置"))


class DataSource(models.Model):
    name = models.CharField(max_length=256, verbose_name=_("数据源名称"))
    code = models.CharField(max_length=256)
    status = models.CharField(max_length=256, verbose_name=_("数据源状态"))
    owner = models.CharField(max_length=256, verbose_name=_("归属租户"))
    plugin_id = models.IntegerField(verbose_name=_("数据源插件id"))
    plugin_config = models.JSONField(verbose_name=_("数据源配置"))


class DataSourceUser(models.Model):
    data_source_id = models.CharField(max_length=256, verbose_name=_("数据源ID"))
    username = models.CharField(verbose_name=_("用户名"), max_length=255)
    display_name = models.CharField(max_length=256, verbose_name=_("全名"))
    email = models.EmailField(verbose_name=_("邮箱"), null=True, blank=True, default="", max_length=255)
    telephone = models.CharField(verbose_name=_("手机号码"), null=True, blank=True, default="", max_length=255)
    logo = models.TextField(max_length=256, null=True, blank=True, default="")
    staff_status = models.CharField(max_length=256, default="")
    is_deleted = models.BooleanField(default=False)
    password = models.CharField(verbose_name=_("用户密码"), null=True, blank=True, default="", max_length=255)
