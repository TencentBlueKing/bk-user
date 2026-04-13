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
from django.utils.translation import gettext_lazy as _

from bkuser.apps.data_source.constants import DataSourceTypeEnum, UsernameConflictStrategy
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
class DataSourceManager(models.Manager.from_queryset(DataSourceQuerySet)):  # type: ignore
    def check_username_affix_unique(
        self, tenant_id: str, prefix: str, suffix: str, exclude_id: int | None = None
    ) -> None:
        """校验同租户下 ADD_AFFIX 策略的用户名前后缀唯一性"""
        qs = self.filter(owner_tenant_id=tenant_id, type=DataSourceTypeEnum.REAL)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)

        for ds in qs:
            cfg = ds.get_conflict_config()
            if cfg.strategy != UsernameConflictStrategy.ADD_AFFIX:
                continue
            if cfg.prefix == prefix and cfg.suffix == suffix:
                raise ValueError(_("当前租户已存在相同用户名前后缀的数据源"))


class DataSourceUserManager(models.Manager):
    def is_username_exists(
        self, data_source_ids: List[int], username: str, excluded_data_source_user_id: int | None = None
    ) -> bool:
        queryset = self.filter(data_source_id__in=data_source_ids, username=username)
        if excluded_data_source_user_id:
            queryset = queryset.exclude(id=excluded_data_source_user_id)
        return queryset.exists()
