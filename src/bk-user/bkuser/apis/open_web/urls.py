# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
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

from django.urls import include, path

from . import views

urlpatterns = [
    path(
        "tenant/",
        include(
            [
                path(
                    "data-source-owner-tenants/",
                    views.DataSourceOwnerTenantListApi.as_view(),
                    name="open_web.data_source_owner_tenant.list",
                ),
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
                path(
                    "users/-/search/",
                    views.TenantUserSearchApi.as_view(),
                    name="open_web.tenant_user.search",
                ),
                path(
                    "users/-/lookup/",
                    views.TenantUserLookupApi.as_view(),
                    name="open_web.tenant_user.lookup",
                ),
                path(
                    "departments/-/search/",
                    views.TenantDepartmentSearchApi.as_view(),
                    name="open_web.tenant_department.search",
                ),
                path(
                    "departments/-/lookup/",
                    views.TenantDepartmentLookupApi.as_view(),
                    name="open_web.tenant_department.lookup",
                ),
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
                path(
                    "virtual-users/",
                    views.VirtualUserListApi.as_view(),
                    name="open_web.tenant.virtual_user.list",
                ),
                path(
                    "users/<str:id>/language/",
                    views.TenantUserLanguageUpdateApi.as_view(),
                    name="open_web.tenant_user.language.update",
                ),
            ]
        ),
    ),
]
