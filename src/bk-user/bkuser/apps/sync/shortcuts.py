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

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.sync.constants import SyncTaskTrigger
from bkuser.apps.sync.data_models import TenantSyncOptions
from bkuser.apps.sync.managers import TenantSyncManager
from bkuser.apps.tenant.constants import CollaborationStrategyStatus
from bkuser.apps.tenant.models import CollaborationStrategy

logger = logging.getLogger(__name__)


def start_collaboration_tenant_sync(strategy: CollaborationStrategy):
    """根据策略决策，若通过则立即异步执行协同租户同步任务"""

    if strategy.source_status != CollaborationStrategyStatus.ENABLED:
        logger.info("collaboration strategy %s is not enabled by source, skip sync...", strategy.id)
        return

    if strategy.target_status != CollaborationStrategyStatus.ENABLED:
        logger.info("collaboration strategy %s is not enabled by target, skip sync...", strategy.id)
        return

    data_source = DataSource.objects.filter(
        owner_tenant_id=strategy.source_tenant_id, type=DataSourceTypeEnum.REAL
    ).first()
    if not data_source:
        logger.info(
            "collaboration strategy %s source tenant %s didn't have real user data source, skip sync...",
            strategy.id,
            strategy.source_tenant_id,
        )
        return

    sync_opts = TenantSyncOptions(operator=strategy.updater, async_run=True, trigger=SyncTaskTrigger.MANUAL)
    TenantSyncManager(data_source, strategy.target_tenant_id, sync_opts).execute()
