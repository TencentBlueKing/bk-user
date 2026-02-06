# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from typing import List

from django.db import models, transaction

from bkuser.plugins.models import BasePluginConfig


class DataSourceQuerySet(models.QuerySet):
    """数据源 QuerySet 类"""

    @transaction.atomic()
    def create(self, **kwargs):
        if "plugin_config" not in kwargs:
            return super().create(**kwargs)

        plugin_cfg = kwargs.pop("plugin_config")
        assert isinstance(plugin_cfg, BasePluginConfig)

        data_source = super().create(**kwargs)
        data_source.set_plugin_cfg(plugin_cfg)
        return data_source


# 数据源管理器类
DataSourceManager = models.Manager.from_queryset(DataSourceQuerySet)


class DataSourceUserManager(models.Manager):
    def is_username_exists(
        self, data_source_ids: List[int], username: str, excluded_data_source_user_id: int | None = None
    ) -> bool:
        queryset = self.filter(data_source_id__in=data_source_ids, username=username)
        if excluded_data_source_user_id:
            queryset = queryset.exclude(id=excluded_data_source_user_id)
        return queryset.exists()
