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
from django.utils import timezone

from bkuser.apps.data_source.models import DataSource
from bkuser.apps.sync.constants import SyncTaskStatus
from bkuser.apps.sync.models import DataSourceSyncTask, TenantSyncTask
from bkuser.apps.sync.signals import post_sync_data_source
from bkuser.apps.sync.syncers import (
    DataSourceDepartmentSyncer,
    DataSourceUserSyncer,
    TenantDepartmentSyncer,
    TenantUserSyncer,
)
from bkuser.apps.tenant.models import Tenant
from bkuser.plugins.base import get_plugin_cfg_cls, get_plugin_cls

logger = logging.getLogger(__name__)


class DataSourceSyncTaskRunner:
    """
    数据源同步任务执行器

    FIXME (su) 1. 细化同步异常处理，2. 后续支持软删除后，需要重构同步逻辑
    """

    def __init__(self, task: DataSourceSyncTask, plugin_init_extra_kwargs: Dict[str, Any]):
        self.task = task
        self.data_source = DataSource.objects.get(id=self.task.data_source_id)
        self._initial_plugin(plugin_init_extra_kwargs)

    def run(self):
        logger.info("start sync data source, task_id: %s, data_source_id: %s", self.task.id, self.task.data_source_id)
        with transaction.atomic():
            try:
                self._sync_departments()
                self._sync_users()
            except Exception:
                logger.exception("data source sync failed! task_id: %s", self.task.id)
                self._update_task_status(SyncTaskStatus.FAILED)
                raise

            logger.info("data source sync success! task_id: %s", self.task.id)
            self._update_task_status(SyncTaskStatus.SUCCESS)

        self._send_signal()

    def _initial_plugin(self, plugin_init_extra_kwargs: Dict[str, Any]):
        """初始化数据源插件"""
        plugin_config = self.data_source.plugin_config
        PluginCfgCls = get_plugin_cfg_cls(self.data_source.plugin_id)  # noqa: N806
        if PluginCfgCls is not None:
            plugin_config = PluginCfgCls(**plugin_config)

        PluginCls = get_plugin_cls(self.data_source.plugin_id)  # noqa: N806
        self.plugin = PluginCls(plugin_config, **plugin_init_extra_kwargs)

    def _sync_departments(self):
        """同步部门信息"""
        departments = self.plugin.fetch_departments()
        DataSourceDepartmentSyncer(self.task, self.data_source, departments).sync()

    def _sync_users(self):
        """同步用户信息"""
        users = self.plugin.fetch_users()
        DataSourceUserSyncer(self.task, self.data_source, users).sync()

    def _send_signal(self):
        """发送数据源同步完成信号，触发后续流程"""
        post_sync_data_source.send(sender=self.__class__, data_source=self.data_source)

    def _update_task_status(self, status: SyncTaskStatus):
        """任务正常完成后更新 task 状态"""
        self.task.status = status.value
        self.task.duration = timezone.now() - self.task.start_at
        self.task.save(update_fields=["status", "duration", "updated_at"])


class TenantSyncTaskRunner:
    """
    租户数据同步任务执行器

    FIXME (su) 1. 细化同步异常处理，2. 后续支持软删除后，需要重构同步逻辑
    """

    def __init__(self, task: TenantSyncTask):
        self.task = task
        self.data_source = DataSource.objects.get(id=task.data_source_id)
        self.tenant = Tenant.objects.get(id=task.tenant_id)

    def run(self):
        logger.info(
            "start sync tenant, task_id: %s, data_source_id: %s, tenant_id: %s",
            self.task.id,
            self.data_source.id,
            self.tenant.id,
        )
        with transaction.atomic():
            try:
                self._sync_departments()
                self._sync_users()
            except Exception:
                logger.exception("tenant sync failed! task_id: %s", self.task.id)
                self._update_task_status(SyncTaskStatus.FAILED)
                raise

            logger.info("tenant sync success! task_id: %s", self.task.id)
            self._update_task_status(SyncTaskStatus.SUCCESS)

    def _sync_departments(self):
        """同步部门信息"""
        TenantDepartmentSyncer(self.task, self.data_source, self.tenant).sync()

    def _sync_users(self):
        """同步用户信息"""
        TenantUserSyncer(self.task, self.data_source, self.tenant).sync()

    def _update_task_status(self, status: SyncTaskStatus):
        """任务正常完成后更新 task 状态"""
        self.task.status = status.value
        self.task.duration = timezone.now() - self.task.start_at
        self.task.save(update_fields=["status", "duration", "updated_at"])
