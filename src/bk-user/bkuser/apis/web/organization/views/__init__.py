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

from .departments import (
    OptionalTenantDepartmentListApi,
    TenantDepartmentListCreateApi,
    TenantDepartmentSearchApi,
    TenantDepartmentUpdateDestroyApi,
)
from .tenants import (
    CollaborativeTenantListApi,
    CurrentTenantRetrieveApi,
    TenantRequiredUserFieldListApi,
)
from .users import (
    OptionalTenantUserListApi,
    TenantUserBatchCopyApi,
    TenantUserBatchCreateApi,
    TenantUserBatchDeleteApi,
    TenantUserBatchMoveApi,
    TenantUserListCreateApi,
    TenantUserOrganizationPathListApi,
    TenantUserPasswordResetApi,
    TenantUserRetrieveUpdateDestroyApi,
    TenantUserSearchApi,
    TenantUserStatusUpdateApi,
)

__all__ = [
    # 租户
    "CurrentTenantRetrieveApi",
    "CollaborativeTenantListApi",
    "TenantRequiredUserFieldListApi",
    # 租户部门
    "TenantDepartmentListCreateApi",
    "TenantDepartmentUpdateDestroyApi",
    "TenantDepartmentSearchApi",
    "OptionalTenantDepartmentListApi",
    # 租户用户
    "OptionalTenantUserListApi",
    "TenantUserSearchApi",
    "TenantUserListCreateApi",
    "TenantUserRetrieveUpdateDestroyApi",
    "TenantUserPasswordResetApi",
    "TenantUserOrganizationPathListApi",
    "TenantUserStatusUpdateApi",
    "TenantUserBatchCreateApi",
    "TenantUserBatchCopyApi",
    "TenantUserBatchMoveApi",
    "TenantUserBatchDeleteApi",
]
