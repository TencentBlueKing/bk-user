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
        "collaborative-tenants/",
        views.CollaborativeTenantListApi.as_view(),
        name="organization.collaborative_tenant.list",
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
    # 数据源部门列表
    path(
        "data-sources/departments/",
        views.DataSourceDepartmentListApi.as_view(),
        name="organization.data_source_department.list",
    ),
    # 数据源用户列表
    path(
        "data-sources/users/",
        views.DataSourceUserListApi.as_view(),
        name="organization.data_source_user.list",
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
]
