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


class TimestampedModel(models.Model):
    """Model with 'created' and 'updated' fields."""

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AdvancedModelManager(models.Manager):
    def enable_or_disable(self, is_enable: bool, *args, **kwargs):
        if is_enable:
            enable_param = kwargs.pop("enable_param", {"enabled": True})
            self.get_queryset().filter(*args, **kwargs).update(**enable_param)
            return
        disable_param = kwargs.pop("disable_param", {"enabled": False})
        self.get_queryset().filter(*args, **kwargs).update(**disable_param)
        return
