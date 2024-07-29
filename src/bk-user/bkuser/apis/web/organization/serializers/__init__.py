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

from .departments import (
    OptionalTenantDepartmentListInputSLZ,
    OptionalTenantDepartmentListOutputSLZ,
    TenantDepartmentCreateInputSLZ,
    TenantDepartmentCreateOutputSLZ,
    TenantDepartmentListInputSLZ,
    TenantDepartmentListOutputSLZ,
    TenantDepartmentSearchInputSLZ,
    TenantDepartmentSearchOutputSLZ,
    TenantDepartmentUpdateInputSLZ,
)
from .relations import (
    TenantDeptUserRelationBatchCreateInputSLZ,
    TenantDeptUserRelationBatchDeleteInputSLZ,
    TenantDeptUserRelationBatchPatchInputSLZ,
    TenantDeptUserRelationBatchUpdateInputSLZ,
)
from .tenants import (
    RequiredTenantUserFieldOutputSLZ,
    TenantListOutputSLZ,
    TenantRetrieveOutputSLZ,
)
from .users import (
    OptionalTenantUserListInputSLZ,
    OptionalTenantUserListOutputSLZ,
    TenantUserAccountExpiredAtUpdateInputSLZ,
    TenantUserBatchCreateInputSLZ,
    TenantUserBatchCreatePreviewInputSLZ,
    TenantUserBatchCreatePreviewOutputSLZ,
    TenantUserBatchDeleteInputSLZ,
    TenantUserCreateInputSLZ,
    TenantUserCreateOutputSLZ,
    TenantUserListInputSLZ,
    TenantUserListOutputSLZ,
    TenantUserOrganizationPathOutputSLZ,
    TenantUserPasswordResetInputSLZ,
    TenantUserPasswordRuleRetrieveOutputSLZ,
    TenantUserRetrieveOutputSLZ,
    TenantUserSearchInputSLZ,
    TenantUserSearchOutputSLZ,
    TenantUserStatusUpdateOutputSLZ,
    TenantUserUpdateInputSLZ,
)

__all__ = [
    # 租户
    "TenantListOutputSLZ",
    "TenantRetrieveOutputSLZ",
    "RequiredTenantUserFieldOutputSLZ",
    # 租户部门
    "TenantDepartmentListInputSLZ",
    "TenantDepartmentListOutputSLZ",
    "TenantDepartmentCreateInputSLZ",
    "TenantDepartmentCreateOutputSLZ",
    "TenantDepartmentUpdateInputSLZ",
    "TenantDepartmentSearchInputSLZ",
    "TenantDepartmentSearchOutputSLZ",
    "OptionalTenantDepartmentListInputSLZ",
    "OptionalTenantDepartmentListOutputSLZ",
    # 租户用户
    "OptionalTenantUserListInputSLZ",
    "OptionalTenantUserListOutputSLZ",
    "TenantUserSearchInputSLZ",
    "TenantUserSearchOutputSLZ",
    "TenantUserListInputSLZ",
    "TenantUserListOutputSLZ",
    "TenantUserCreateInputSLZ",
    "TenantUserCreateOutputSLZ",
    "TenantUserRetrieveOutputSLZ",
    "TenantUserUpdateInputSLZ",
    "TenantUserPasswordRuleRetrieveOutputSLZ",
    "TenantUserPasswordResetInputSLZ",
    "TenantUserOrganizationPathOutputSLZ",
    "TenantUserStatusUpdateOutputSLZ",
    "TenantUserBatchCreateInputSLZ",
    "TenantUserBatchCreatePreviewInputSLZ",
    "TenantUserBatchCreatePreviewOutputSLZ",
    "TenantUserBatchDeleteInputSLZ",
    "TenantUserAccountExpiredAtUpdateInputSLZ",
    # 租户部门 - 用户关系
    "TenantDeptUserRelationBatchCreateInputSLZ",
    "TenantDeptUserRelationBatchUpdateInputSLZ",
    "TenantDeptUserRelationBatchPatchInputSLZ",
    "TenantDeptUserRelationBatchDeleteInputSLZ",
]
