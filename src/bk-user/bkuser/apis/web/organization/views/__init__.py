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

from .departments import (
    OptionalTenantDepartmentListApi,
    TenantDepartmentListCreateApi,
    TenantDepartmentParentUpdateApi,
    TenantDepartmentSearchApi,
    TenantDepartmentUpdateDestroyApi,
)
from .relations import (
    TenantDeptUserRelationBatchCreateApi,
    TenantDeptUserRelationBatchDeleteApi,
    TenantDeptUserRelationBatchUpdateApi,
)
from .tenants import (
    CollaborationTenantListApi,
    CurrentTenantRetrieveApi,
    RequiredTenantUserFieldListApi,
)
from .users import (
    OptionalTenantUserListApi,
    TenantUserAccountExpiredAtBatchUpdateApi,
    TenantUserAccountExpiredAtUpdateApi,
    TenantUserBatchCreateApi,
    TenantUserBatchCreatePreviewApi,
    TenantUserBatchDeleteApi,
    TenantUserCustomFieldBatchUpdateApi,
    TenantUserLeaderBatchUpdateApi,
    TenantUserListCreateApi,
    TenantUserOrganizationPathListApi,
    TenantUserPasswordBatchResetApi,
    TenantUserPasswordResetApi,
    TenantUserPasswordRuleRetrieveApi,
    TenantUserRetrieveUpdateDestroyApi,
    TenantUserSearchApi,
    TenantUserStatusBatchUpdateApi,
    TenantUserStatusUpdateApi,
)

__all__ = [
    # 租户
    "CurrentTenantRetrieveApi",
    "CollaborationTenantListApi",
    "RequiredTenantUserFieldListApi",
    # 租户部门
    "TenantDepartmentListCreateApi",
    "TenantDepartmentUpdateDestroyApi",
    "TenantDepartmentSearchApi",
    "OptionalTenantDepartmentListApi",
    "TenantDepartmentParentUpdateApi",
    # 租户用户
    "OptionalTenantUserListApi",
    "TenantUserSearchApi",
    "TenantUserListCreateApi",
    "TenantUserRetrieveUpdateDestroyApi",
    "TenantUserPasswordRuleRetrieveApi",
    "TenantUserPasswordResetApi",
    "TenantUserOrganizationPathListApi",
    "TenantUserStatusUpdateApi",
    "TenantUserBatchCreateApi",
    "TenantUserBatchCreatePreviewApi",
    "TenantUserBatchDeleteApi",
    "TenantUserStatusBatchUpdateApi",
    "TenantUserAccountExpiredAtBatchUpdateApi",
    "TenantUserCustomFieldBatchUpdateApi",
    "TenantUserLeaderBatchUpdateApi",
    "TenantUserPasswordBatchResetApi",
    "TenantUserAccountExpiredAtUpdateApi",
    # 租户部门 - 用户关系
    "TenantDeptUserRelationBatchCreateApi",
    "TenantDeptUserRelationBatchUpdateApi",
    "TenantDeptUserRelationBatchDeleteApi",
]
