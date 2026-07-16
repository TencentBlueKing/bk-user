# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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

from django.urls import include, path

from . import views

# ==================== 租户/数据源 ====================
_tenant_patterns = [
    path(
        "data-source-owner-tenants/",
        views.DataSourceOwnerTenantListApi.as_view(),
        name="open_web.data_source_owner_tenant.list",
    ),
]

# ==================== 当前用户（本租户实名） ====================
_current_user_patterns = [
    path(
        "current-user/language/",
        views.CurrentUserLanguageUpdateApi.as_view(),
        name="open_web.tenant.current_user.language.update",
    ),
]

# ==================== 用户（本租户实名 + 本租户虚拟 + 协同租户实名） ====================
# 场景：调用方持有 bk_username 需要回显用户信息，但不知道该用户属于哪种类型，必须跨所有类型查询
_user_all_scope_patterns = [
    path(
        "users/-/display_info/",
        views.TenantUserDisplayInfoListApi.as_view(),
        name="open_web.tenant_user.display_info.list",
    ),
    path(
        "users/<str:id>/display_info/",
        views.TenantUserDisplayInfoRetrieveApi.as_view(),
        name="open_web.tenant_user.display_info.retrieve",
    ),
    path("users/-/lookup/", views.TenantUserLookupApi.as_view(), name="open_web.tenant_user.lookup"),
]

# ==================== 用户（本租户实名 + 协同租户实名） ====================
_user_patterns = [
    path("users/-/search/", views.TenantUserSearchApi.as_view(), name="open_web.tenant_user.search"),
]

# ==================== 部门（本租户实名 + 协同租户实名） ====================
_department_patterns = [
    path("departments/-/search/", views.TenantDepartmentSearchApi.as_view(), name="open_web.tenant_department.search"),
    path("departments/-/lookup/", views.TenantDepartmentLookupApi.as_view(), name="open_web.tenant_department.lookup"),
    path(
        "departments/<int:id>/children/",
        views.TenantDepartmentChildrenListApi.as_view(),
        name="open_web.tenant_department.child.list",
    ),
    path(
        "departments/<int:id>/users/",
        views.TenantDepartmentUserListApi.as_view(),
        name="open_web.tenant_department.user.list",
    ),
]

# ==================== 虚拟用户（本租户虚拟） ====================
_virtual_user_patterns = [
    path("virtual-users/", views.VirtualUserListApi.as_view(), name="open_web.tenant.virtual_user.list"),
    path("virtual-users/-/search/", views.VirtualUserSearchApi.as_view(), name="open_web.tenant.virtual_user.search"),
]

# ==================== 汇总 ====================
urlpatterns = [
    path(
        "tenant/",
        include(
            _tenant_patterns
            + _current_user_patterns
            + _user_all_scope_patterns
            + _user_patterns
            + _department_patterns
            + _virtual_user_patterns
        ),
    ),
]
