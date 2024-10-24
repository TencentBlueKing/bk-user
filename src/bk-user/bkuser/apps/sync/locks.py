# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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

import logging

from django.conf import settings
from redis.exceptions import LockError

from bkuser.common.locks import LockType, RedisLock

logger = logging.getLogger(__name__)


class DataSourceSyncTaskLock:
    """数据源同步任务锁"""

    def __init__(self, data_source_id: int, timeout: int):
        """
        :param data_source_id: 数据源 ID
        :param timeout: 锁超时时间
        """
        self._lock = RedisLock(
            LockType.DATA_SOURCE_SYNC,
            suffix=f"data_source:{data_source_id}",
            timeout=timeout,
            # 抢不到锁就失败，不阻塞
            blocking=False,
        )

    def acquire(self) -> bool:
        return self._lock.acquire()

    def release(self):
        try:
            return self._lock.release()
        except LockError:
            logger.exception("failed to release data source sync lock")


class TenantSyncTaskLock:
    """租户同步任务锁"""

    def __init__(self, tenant_id: str, data_source_id: int):
        """
        :param tenant_id: 租户 ID
        :param data_source_id: 数据源 ID
        """
        self._lock = RedisLock(
            LockType.TENANT_SYNC,
            suffix=f"tenant:{tenant_id}:data_source:{data_source_id}",
            timeout=settings.TENANT_SYNC_DEFAULT_TIMEOUT,
            # 抢不到锁就失败，不阻塞
            blocking=False,
        )

    def acquire(self) -> bool:
        return self._lock.acquire()

    def release(self):
        try:
            return self._lock.release()
        except LockError:
            logger.exception("failed to release tenant sync lock")
