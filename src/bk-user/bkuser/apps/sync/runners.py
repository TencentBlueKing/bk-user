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
import logging
from typing import Any, Dict

from django.db import transaction

from bkuser.apps.data_source.models import DataSource
from bkuser.apps.sync.context import DataSourceSyncTaskContext, TenantSyncTaskContext
from bkuser.apps.sync.models import DataSourceSyncTask, TenantSyncTask
from bkuser.apps.sync.signals import post_sync_data_source
from bkuser.apps.sync.syncers import (
    DataSourceDepartmentSyncer,
    DataSourceUserSyncer,
    TenantDepartmentSyncer,
    TenantUserSyncer,
)
from bkuser.apps.tenant.models import Tenant
from bkuser.plugins.base import get_plugin_cls

logger = logging.getLogger(__name__)


class DataSourceSyncTaskRunner:
    """
    数据源同步任务执行器

    TODO (su) 后续支持软删除后，需要更新同步逻辑
    """

    def __init__(self, task: DataSourceSyncTask, plugin_init_extra_kwargs: Dict[str, Any]):
        self.task = task
        self.data_source = DataSource.objects.get(id=self.task.data_source_id)
        self._initial_plugin(plugin_init_extra_kwargs)

    def run(self):
        with DataSourceSyncTaskContext(self.task) as ctx, transaction.atomic():
            self._sync_departments(ctx)
            self._sync_users(ctx)

        self._send_signal()

    def _initial_plugin(self, plugin_init_extra_kwargs: Dict[str, Any]):
        """初始化数据源插件"""
        plugin_cfg = self.data_source.get_plugin_cfg()

        PluginCls = get_plugin_cls(self.data_source.plugin_id)  # noqa: N806
        self.plugin = PluginCls(plugin_cfg, **plugin_init_extra_kwargs)

    def _sync_departments(self, ctx: DataSourceSyncTaskContext):
        """同步部门信息"""
        departments = self.plugin.fetch_departments()
        DataSourceDepartmentSyncer(ctx, self.data_source, departments).sync()

    def _sync_users(self, ctx: DataSourceSyncTaskContext):
        """同步用户信息"""
        DataSourceUserSyncer(
            ctx=ctx,
            data_source=self.data_source,
            raw_users=self.plugin.fetch_users(),
            overwrite=bool(self.task.extras.get("overwrite", False)),
            incremental=bool(self.task.extras.get("incremental", False)),
        ).sync()

    def _send_signal(self):
        """发送数据源同步完成信号，触发后续流程"""
        post_sync_data_source.send(sender=self.__class__, data_source=self.data_source)


class TenantSyncTaskRunner:
    """
    租户数据同步任务执行器

    TODO (su) 后续支持软删除后，需要更新同步逻辑
    """

    def __init__(self, task: TenantSyncTask):
        self.task = task
        self.data_source = DataSource.objects.get(id=task.data_source_id)
        self.tenant = Tenant.objects.get(id=task.tenant_id)

    def run(self):
        with TenantSyncTaskContext(self.task) as ctx, transaction.atomic():
            self._sync_departments(ctx)
            self._sync_users(ctx)

    def _sync_departments(self, ctx: TenantSyncTaskContext):
        """同步部门信息"""
        TenantDepartmentSyncer(ctx, self.data_source, self.tenant).sync()

    def _sync_users(self, ctx: TenantSyncTaskContext):
        """同步用户信息"""
        TenantUserSyncer(ctx, self.data_source, self.tenant).sync()
