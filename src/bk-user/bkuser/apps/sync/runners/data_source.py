# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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

# ignore custom logger must use %s string format in this file
# ruff: noqa: G004
import logging
from typing import Any, Dict

from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.sync.constants import DataSourceSyncObjectType
from bkuser.apps.sync.contexts import DataSourceSyncTaskContext
from bkuser.apps.sync.models import DataSourceSyncTask
from bkuser.apps.sync.signals import post_sync_data_source
from bkuser.apps.sync.syncers import (
    DataSourceDepartmentRelationSyncer,
    DataSourceDepartmentSyncer,
    DataSourceUserDeptRelationSyncer,
    DataSourceUserLeaderRelationSyncer,
    DataSourceUserSyncer,
)
from bkuser.apps.sync.validators import DataSourceUserExtrasUniqueValidator
from bkuser.apps.tenant.constants import TenantStatus
from bkuser.apps.tenant.models import Tenant
from bkuser.plugins.base import get_plugin_cls

logger = logging.getLogger(__name__)


class DataSourceSyncTaskRunner:
    """数据源同步任务执行器"""

    def __init__(self, task: DataSourceSyncTask, plugin_init_extra_kwargs: Dict[str, Any]):
        self.task = task
        self.data_source = DataSource.objects.get(id=self.task.data_source_id)
        self.plugin_init_extra_kwargs = plugin_init_extra_kwargs

    def run(self):
        if self._need_skip_sync():
            return

        with DataSourceSyncTaskContext(self.task) as ctx:
            self._initial_plugin(ctx, self.plugin_init_extra_kwargs)
            self._sync_departments(ctx)
            self._sync_users(ctx)
            self._validate_unique_fields(ctx)
            self._send_signal(ctx)

    def _need_skip_sync(self) -> bool:
        """租户不是启用状态，需要跳过同步"""
        if not Tenant.objects.filter(id=self.data_source.owner_tenant_id, status=TenantStatus.ENABLED).exists():
            logger.warning(
                "data source %s's owner tenant %s isn't enabled, skip sync...",
                self.data_source.id,
                self.data_source.owner_tenant_id,
            )
            return True

        return False

    def _initial_plugin(self, ctx: DataSourceSyncTaskContext, plugin_init_extra_kwargs: Dict[str, Any]):
        """初始化数据源插件"""
        plugin_cfg = self.data_source.get_plugin_cfg()

        PluginCls = get_plugin_cls(self.data_source.plugin_id)  # noqa: N806
        self.plugin = PluginCls(plugin_cfg, ctx.logger, **plugin_init_extra_kwargs)

    def _sync_departments(self, ctx: DataSourceSyncTaskContext):
        """同步部门信息"""
        raw_departments = self.plugin.fetch_departments()
        ctx.logger.info(f"receive {len(raw_departments)} departments from data source plugin")

        kwargs = {
            "ctx": ctx,
            "data_source": self.data_source,
            "raw_departments": raw_departments,
            "overwrite": bool(self.task.extras.get("overwrite", False)),
            "incremental": bool(self.task.extras.get("incremental", False)),
        }
        # 部门主体
        DataSourceDepartmentSyncer(**kwargs).sync()  # type: ignore
        ctx.synced_obj_types.add(DataSourceSyncObjectType.DEPARTMENT)
        # 部门间关系
        DataSourceDepartmentRelationSyncer(**kwargs).sync()  # type: ignore
        ctx.synced_obj_types.add(DataSourceSyncObjectType.DEPARTMENT_RELATION)

        ctx.logger.info("succeed to sync departments and their relations from data source plugin")

    def _sync_users(self, ctx: DataSourceSyncTaskContext):
        """同步用户信息"""
        raw_users = self.plugin.fetch_users()
        ctx.logger.info(f"receive {len(raw_users)} users from data source plugin")

        kwargs = {
            "ctx": ctx,
            "data_source": self.data_source,
            "raw_users": raw_users,
            "overwrite": bool(self.task.extras.get("overwrite", False)),
            "incremental": bool(self.task.extras.get("incremental", False)),
        }

        # Q: 为什么不能在使用的地方现查？直接 DB 查询获取 “同步前存量” 的用户 ID 集合？
        # A: 这份数据主要是给不覆盖（overwrite=False）的场景使用的，
        #    目的是避免修改到同步前已存在用户的关联边（不删除 / 追加）
        #    如果在使用的地方再查询，会因为这时用户主体已经完成同步，
        #    导致出现所有用户都是已存在的用户，因而不为刚同步的用户添加关联边的问题
        #
        # ref: https://github.com/TencentBlueKing/bk-user/pull/1904/files
        exists_user_ids = set(DataSourceUser.objects.filter(data_source=self.data_source).values_list("id", flat=True))
        # 用户主体
        DataSourceUserSyncer(**kwargs).sync()  # type: ignore
        ctx.synced_obj_types.add(DataSourceSyncObjectType.USER)
        # 用户 Leader 关系
        DataSourceUserLeaderRelationSyncer(exists_user_ids_before_sync=exists_user_ids, **kwargs).sync()  # type: ignore
        ctx.synced_obj_types.add(DataSourceSyncObjectType.USER_LEADER_RELATION)
        # 用户部门关系
        DataSourceUserDeptRelationSyncer(exists_user_ids_before_sync=exists_user_ids, **kwargs).sync()  # type: ignore
        ctx.synced_obj_types.add(DataSourceSyncObjectType.USER_DEPARTMENT_RELATION)

        ctx.logger.info("succeed to sync users and their leader & dept relations from data source plugin")

    def _validate_unique_fields(self, ctx: DataSourceSyncTaskContext):
        """对有唯一性要求的自定义字段的校验"""
        DataSourceUserExtrasUniqueValidator(self.data_source, ctx.logger).validate()

    def _send_signal(self, ctx: DataSourceSyncTaskContext):
        """若符合准出条件，则发送数据源同步完成信号，触发后续流程

        资源同步顺序：部门 -> 部门间关系 -> 用户 -> 用户 Leader 关系 -> 用户部门关系

        同步失败可能有下面几种场景：

          1：部门同步失败，被回滚 -> 数据都不变，不需要同步到租户

          2：部门同步成功，但是部门关系同步失败
               -> 部门数据变，用户数据不变，此时不会同步到租户
               具体影响：部分用户无法获取部门信息（部门被删除，导致有边无节点）

          3：部门 & 部门关系同步成功，用户同步失败，用户数据被回滚 -> 效果同场景 2

          4：部门 & 部门关系 & 用户同步成功，用户 Leader 关系同步失败
               -> 会同步到租户，但用户 Leader，部门关联边是老数据
               具体影响：部分用户无法获取 Leader / 部门信息（Leader / 部门被删除，导致有边无节点）

          5：部门 & 部门关系 & 用户 & 用户 Leader 关系同步成功，用户部门关系同步失败
               -> 会同步到租户，但用户部门关联边是老数据
               具体影响：部分用户无法获取部门信息（部门被删除，导致有边无节点）

         注意：其中场景 2 出现概率极低（原因是 mptt 树是直接重建的，除非 tree_id 分配到 int 上限导致失败，需运维介入）
        """
        ctx.logger.info(f"current synced object types is {[t.value for t in ctx.synced_obj_types]}")

        if (
            DataSourceSyncObjectType.DEPARTMENT not in ctx.synced_obj_types
            or DataSourceSyncObjectType.USER not in ctx.synced_obj_types
        ):
            ctx.logger.error("departments or users haven't been synced, skip sync tenant...")
            return

        # 若用户 & 部门主体完成同步，即可触发租户同步流程
        post_sync_data_source.send(sender=self.__class__, data_source=self.data_source)
        ctx.logger.info("signal post_sync_data_source sent...")
