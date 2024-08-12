# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from .data_source_department import (
    DataSourceDepartmentRelationSyncer,
    DataSourceDepartmentSyncer,
)
from .data_source_user import (
    DataSourceUserDeptRelationSyncer,
    DataSourceUserLeaderRelationSyncer,
    DataSourceUserSyncer,
)
from .tenant_department import TenantDepartmentSyncer
from .tenant_user import TenantUserSyncer

__all__ = [
    "DataSourceDepartmentSyncer",
    "DataSourceDepartmentRelationSyncer",
    "DataSourceUserSyncer",
    "DataSourceUserLeaderRelationSyncer",
    "DataSourceUserDeptRelationSyncer",
    "TenantDepartmentSyncer",
    "TenantUserSyncer",
]
