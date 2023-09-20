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

from bkuser.apps.tenant.models import Tenant
from bkuser.apps.tenant_setting.constants import UserFieldDataType
from bkuser.common.models import TimestampedModel


class UserBuiltinField(TimestampedModel):
    """用户内置字段"""

    name = models.CharField("字段名称", unique=True, max_length=128)
    display_name = models.CharField("展示用名称", unique=True, max_length=128)
    data_type = models.CharField("数据类型", choices=UserFieldDataType.get_choices(), max_length=32)
    required = models.BooleanField("是否必填")
    unique = models.BooleanField("是否唯一")
    default = models.JSONField("默认值", default="")
    options = models.JSONField("配置项", default={})


class UserCustomField(TimestampedModel):
    """租户用户自定义字段"""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, db_constraint=False)
    name = models.CharField("字段名称", max_length=128)
    display_name = models.CharField("展示用名称", max_length=128)
    data_type = models.CharField("数据类型", choices=UserFieldDataType.get_choices(), max_length=32)
    required = models.BooleanField("是否必填")
    default = models.JSONField("默认值", default="")
    options = models.JSONField("配置项", default={})

    class Meta:
        unique_together = [
            ("name", "tenant"),
            ("display_name", "tenant"),
        ]
