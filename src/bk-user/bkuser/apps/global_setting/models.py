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

from .constants import GlobalSettingEnum


class GlobalSetting(TimestampedModel):
    """全局配置"""

    id = models.CharField("配置唯一标识", primary_key=True, max_length=64, choices=GlobalSettingEnum.get_choices())
    name = models.CharField("配置名称", unique=True, max_length=128)
    value = models.JSONField("配置项", default=dict)
