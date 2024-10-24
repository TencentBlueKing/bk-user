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

import logging
from collections import defaultdict
from typing import Dict, List, Tuple

from bkuser.apps.data_source.models import DataSourceDepartment, DataSourceUser
from bkuser.apps.sync.constants import DataSourceSyncObjectType, SyncOperation, TenantSyncObjectType
from bkuser.apps.tenant.models import TenantDepartment, TenantUser

logger = logging.getLogger(__name__)

# 二元组对象，用于以何种方式，操作某类对象
SyncOperationObjectType = Tuple[SyncOperation, DataSourceSyncObjectType | TenantSyncObjectType]


class ChangeLogRecorder:
    """变更日志记录器"""

    records: Dict[SyncOperationObjectType, List]

    def __init__(self):
        self.records = defaultdict(list)

    def add(
        self,
        operation: SyncOperation,
        type: DataSourceSyncObjectType | TenantSyncObjectType,
        items: List[DataSourceUser | DataSourceDepartment | TenantUser | TenantDepartment],
    ):
        """添加某类型某操作的变更日志"""
        self.records[(operation, type)].extend(items)

    def get(
        self, operation: SyncOperation, type: DataSourceSyncObjectType | TenantSyncObjectType
    ) -> List[DataSourceUser | DataSourceDepartment | TenantUser | TenantDepartment]:
        """获取某类型某操作的变更日志"""
        return self.records[(operation, type)]
