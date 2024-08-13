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

from django.urls import path

from . import views

urlpatterns = [
    # 当前用户所在租户信息
    path(
        "current-tenant/",
        views.CurrentTenantRetrieveApi.as_view(),
        name="organization.tenant.retrieve",
    ),
    # 协作租户信息
    path(
        "collaboration-tenants/",
        views.CollaborationTenantListApi.as_view(),
        name="organization.collaboration_tenant.list",
    ),
    # 租户用户 - 快速录入必填字段
    path(
        "tenants/required-user-fields/",
        views.RequiredTenantUserFieldListApi.as_view(),
        name="organization.tenant.required_user_field.list",
    ),
    # 租户部门列表
    path(
        "tenants/<str:id>/departments/",
        views.TenantDepartmentListCreateApi.as_view(),
        name="organization.tenant_department.list_create",
    ),
    # 更新 / 删除租户部门
    path(
        "tenants/departments/<str:id>/",
        views.TenantDepartmentUpdateDestroyApi.as_view(),
        name="organization.tenant_department.update_destroy",
    ),
    # 搜索租户部门（含协同数据）
    path(
        "tenants/departments/",
        views.TenantDepartmentSearchApi.as_view(),
        name="organization.tenant_department.search",
    ),
    # 可选租户部门列表（下拉框数据用）
    path(
        "tenants/optional-departments/",
        views.OptionalTenantDepartmentListApi.as_view(),
        name="organization.optional_department.list",
    ),
    # 可选租户用户上级列表（下拉框数据用）
    path(
        "tenants/optional-leaders/",
        views.OptionalTenantUserListApi.as_view(),
        name="organization.optional_leader.list",
    ),
    # 搜索租户用户（含协同数据）
    path(
        "tenants/users/",
        views.TenantUserSearchApi.as_view(),
        name="organization.tenant_user.search",
    ),
    # 租户用户列表 / 创建租户用户
    path(
        "tenants/<str:id>/users/",
        views.TenantUserListCreateApi.as_view(),
        name="organization.tenant_user.list_create",
    ),
    # 获取 / 更新 / 删除租户用户
    path(
        "tenants/users/<str:id>/",
        views.TenantUserRetrieveUpdateDestroyApi.as_view(),
        name="organization.tenant_user.retrieve_update_destroy",
    ),
    # 更新租户用户账号有效期
    path(
        "tenants/users/<str:id>/account-expired-at/",
        views.TenantUserAccountExpiredAtUpdateApi.as_view(),
        name="organization.tenant_user.update_account_expired_at",
    ),
    # 获取租户用户密码规则提示
    path(
        "tenants/users/<str:id>/password-rule/",
        views.TenantUserPasswordRuleRetrieveApi.as_view(),
        name="organization.tenant_user.password_rule",
    ),
    # 重置租户用户密码
    path(
        "tenants/users/<str:id>/password/",
        views.TenantUserPasswordResetApi.as_view(),
        name="organization.tenant_user.password.reset",
    ),
    # 租户用户所属部门组织路径
    path(
        "tenants/users/<str:id>/organization-paths/",
        views.TenantUserOrganizationPathListApi.as_view(),
        name="organization.tenant_user.organization_path.list",
    ),
    # 修改租户用户状态
    path(
        "tenants/users/<str:id>/status/",
        views.TenantUserStatusUpdateApi.as_view(),
        name="organization.tenant_user.status.update",
    ),
    # 批量修改租户用户账号有效期
    path(
        "tenants/users/operations/batch_account_expired_at_update",
        views.TenantUserBatchAccountExpiredAtUpdateApi.as_view(),
        name="organization.tenant_user.batch_account_expired_at_update",
    ),
    # 租户用户 - 快速录入
    path(
        "tenants/users/operations/batch_create/",
        views.TenantUserBatchCreateApi.as_view(),
        name="organization.tenant_user.batch_create",
    ),
    # 租户用户 - 快速录入 - 预览
    path(
        "tenants/users/operations/batch_create_preview/",
        views.TenantUserBatchCreatePreviewApi.as_view(),
        name="organization.tenant_user.batch_create_preview",
    ),
    # 租户用户 - 批量删除
    path(
        "tenants/users/operations/batch_delete/",
        views.TenantUserBatchDeleteApi.as_view(),
        name="organization.tenant_user.batch_delete",
    ),
    # 租户用户 - 批量停用
    path(
        "tenants/users/operations/batch_disable/",
        views.TenantUserBatchDisableApi.as_view(),
        name="organization.tenant_user.batch_disable",
    ),
    # 租户用户 - 批量更新字段信息
    path(
        "tenants/users/operations/batch_field_update/",
        views.TenantUserBatchFieldUpdateApi.as_view(),
        name="organization.tenant_user.batch_field_update",
    ),
    # 租户用户 - 批量修改租户用户上级关系
    path(
        "tenants/users/operations/batch_leader_update/",
        views.TenantUserBatchLeaderUpdateApi.as_view(),
        name="organization.tenant_user.batch_leader_update",
    ),
    # 租户用户 - 批量重置密码
    path(
        "tenants/users/operations/batch_password_reset/",
        views.TenantUserBatchPasswordResetApi.as_view(),
        name="organization.tenant_user.batch_password_reset",
    ),
    # 租户用户 - 从其他组织拉取 / 添加到其他组织
    path(
        "tenants/department-user-relations/operations/batch_create/",
        views.TenantDeptUserRelationBatchCreateApi.as_view(),
        name="organization.tenant_dept_user_relation.batch_create",
    ),
    # 租户用户 - 移动到其他组织 / 清空并加入到其他组织
    path(
        "tenants/department-user-relations/operations/batch_update/",
        views.TenantDeptUserRelationBatchUpdateApi.as_view(),
        name="organization.tenant_dept_user_relation.batch_update",
    ),
    # 租户用户 - 退出当前组织
    path(
        "tenants/department-user-relations/operations/batch_delete/",
        views.TenantDeptUserRelationBatchDeleteApi.as_view(),
        name="organization.tenant_dept_user_relation.batch_delete",
    ),
]
