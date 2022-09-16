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

from django.urls.conf import path

from .views import (
    CategoriesExportTemplateViewSet,
    CategoriesExportViewSet,
    CategoriesSwitchOrderViewSet,
    CategoriesSyncViewSet,
    CategoriesTestConnectionViewSet,
    CategoriesTestFetchDataViewSet,
    CategoryDepartmentsViewSet,
    CategoryListCreateViewSet,
    CategoryMetasViewSet,
    CategoryProfilesViewSet,
    CategorySettingsListViewSet,
    CategorySettingsNamespaceViewSet,
    CategoryUpdateDeleteViewSet,
    DepartmentProfilesViewSet,
    DepartmentRetrieveUpdateDeleteViewSet,
    DepartmentSearchViewSet,
    DepartmentSwitchOrderViewSet,
    DepartmentViewSet,
    FieldsManageableViewSet,
    FieldsOrderViewSet,
    FieldsViewSet,
    FieldsVisibleViewSet,
    GeneralLogViewSet,
    HealthzViewSet,
    LoginInfoViewSet,
    LoginLogExportViewSet,
    LoginLogViewSet,
    PasswordModifyViewSet,
    PasswordResetByTokenViewSet,
    PasswordResetSendMailViewSet,
    ProfileCreateViewSet,
    ProfilesBatchViewSet,
    ProfilesRestorationViewSet,
    ProfilesRetrieveUpdateViewSet,
    ProfilesSearchViewSet,
    SearchViewSet,
    SettingsMetasViewSet,
    SiteFooterViewSet,
    SyncTaskLogViewSet,
    SyncTaskViewSet,
)

urlpatterns = [
    # healthz
    path("healthz/", HealthzViewSet.as_view({"get": "list"}), name="healthz"),
    path("ping/", HealthzViewSet.as_view({"get": "pong"}), name="pong"),
    path("api/footer/", SiteFooterViewSet.as_view({"get": "get"})),
    # sync task
    path(
        "api/v2/sync_task/",
        SyncTaskViewSet.as_view({"get": "list"}),
        name="sync_task.list",
    ),
    path("api/v2/sync_task/<task_id>/logs", SyncTaskLogViewSet.as_view({"get": "list"}), name="sync_task.show_logs"),
    # audit logs
    path("api/v2/audit/operation_logs/", GeneralLogViewSet.as_view({"get": "list"}), name="operation_logs"),
    path("api/v2/audit/login_log/", LoginLogViewSet.as_view({"get": "list"}), name="login_log"),
    path("api/v2/audit/login_log/export/", LoginLogExportViewSet.as_view({"get": "list"}), name="login_log.export"),
    # fields
    path("api/v2/fields/manageable/", FieldsManageableViewSet.as_view({"get": "get"}), name="fields.manageable"),
    path("api/v2/fields/visible/", FieldsVisibleViewSet.as_view({"patch": "patch"}), name="fields.visible"),
    path(
        "api/v2/fields/<int:id>/order/<int:order>/",
        FieldsOrderViewSet.as_view({"patch": "patch"}),
        name="fields.order",
    ),
    path("api/v2/fields/", FieldsViewSet.as_view({"get": "list", "post": "create"}), name="fields.list_create"),
    path(
        "api/v2/fields/<int:id>/",
        FieldsViewSet.as_view({"put": "update", "delete": "delete", "patch": "update"}),
        name="fields.list_create",
    ),
    # profiles
    path("api/v2/me/", LoginInfoViewSet.as_view({"get": "get"}), name="profiles.login_info"),
    path("api/v2/profiles/", ProfileCreateViewSet.as_view({"post": "post"}), name="profiles.create"),
    path(
        "api/v2/profiles/<int:id>/",
        ProfilesRetrieveUpdateViewSet.as_view({"get": "request", "patch": "request"}),
        name="profiles.get_update",
    ),
    path(
        "api/v2/profiles/<int:id>/restoration/",
        ProfilesRestorationViewSet.as_view({"post": "post"}),
        name="profiles.restoration",
    ),
    # categories
    path("api/v2/categories_metas/", CategoryMetasViewSet.as_view({"get": "get"}), name="categories.metas"),
    path(
        "api/v2/categories/", CategoryListCreateViewSet.as_view({"get": "list", "post": "create"}), name="categories"
    ),
    path(
        "api/v2/categories/<int:id>/",
        CategoryUpdateDeleteViewSet.as_view({"patch": "update", "delete": "delete"}),
        name="categories.actions",
    ),
    path(
        "api/v2/categories/<int:id>/test_connection/",
        CategoriesTestConnectionViewSet.as_view({"post": "post"}),
        name="categories.test_connection",
    ),
    path(
        "api/v2/categories/<int:id>/test_fetch_data/",
        CategoriesTestFetchDataViewSet.as_view({"post": "post"}),
        name="categories.test_fetch_data",
    ),
    path(
        "api/v2/categories/<int:id>/export_template/",
        CategoriesExportTemplateViewSet.as_view({"get": "get"}),
        name="categories.export_template",
    ),
    path(
        "api/v2/categories/<int:id>/export/",
        CategoriesExportViewSet.as_view({"get": "get"}),
        name="categories.export",
    ),
    path(
        "api/v2/categories/<int:id>/sync/",
        CategoriesSyncViewSet.as_view({"post": "post"}),
        name="categories.sync",
    ),
    path(
        "api/v2/categories/<int:id>/switch_order/<int:another_id>/",
        CategoriesSwitchOrderViewSet.as_view({"patch": "patch"}),
        name="categories.switch_order",
    ),
    path(
        "api/v2/categories/<int:id>/profiles/",
        CategoryProfilesViewSet.as_view({"get": "list"}),
        name="categories.profiles",
    ),
    path(
        "api/v2/categories/<int:id>/departments/search/",
        CategoryDepartmentsViewSet.as_view({"get": "list"}),
        name="departments.search_in_category",
    ),
    # FIXME: 有没有被调用?
    path(
        "api/v2/categories/<int:id>/settings/",
        CategorySettingsListViewSet.as_view(
            {
                "get": "list",
            }
        ),
        name="category.settings.list",
    ),
    path(
        "api/v2/categories/<int:id>/settings/namespaces/<str:namespace>/",
        CategorySettingsNamespaceViewSet.as_view({"get": "request", "post": "request", "put": "request"}),
        name="category.settings.namespaces",
    ),
    # settings
    path("api/v2/settings/metas/", SettingsMetasViewSet.as_view({"get": "get"}), name="settings.metas"),
    # departments
    path("api/v3/departments/", DepartmentSearchViewSet.as_view({"get": "get"}), name="departments.search"),
    path("api/v3/profiles/", ProfilesSearchViewSet.as_view({"get": "get"}), name="profiles.search"),
    path(
        "api/v2/departments/<int:id>/",
        DepartmentRetrieveUpdateDeleteViewSet.as_view({"get": "request", "delete": "request", "patch": "request"}),
        name="department.actions",
    ),
    path(
        "api/v2/departments/<int:id>/switch_order/<int:another_id>/",
        DepartmentSwitchOrderViewSet.as_view({"patch": "patch"}),
        name="department.switch_order",
    ),
    path(
        "api/v2/departments/<int:id>/profiles/",
        DepartmentProfilesViewSet.as_view({"get": "request", "post": "request"}),
        name="department.profiles",
    ),
    path(
        "api/v2/search/detail/",
        SearchViewSet.as_view({"get": "get"}),
        name="search",
    ),
    # NOTE: 这个接口不应该是 departments, proxy to: /api/v1/web/home/tree/
    path(
        "api/v2/departments/",
        DepartmentViewSet.as_view({"get": "get", "post": "post"}),
        name="departments",
    ),
    path(
        "api/v2/batch/profiles/",
        ProfilesBatchViewSet.as_view({"patch": "request", "delete": "request"}),
        name="profiles.batch.actions",
    ),
    path(
        "api/v1/password/reset/",
        PasswordResetSendMailViewSet.as_view({"post": "post"}),
        name="password.reset.send_mail",
    ),
    path(
        "api/v1/password/reset_by_token/",
        PasswordResetByTokenViewSet.as_view({"post": "post"}),
        name="password.reset.by_token",
    ),
    path(
        "api/v1/password/modify/",
        PasswordModifyViewSet.as_view({"post": "post"}),
        name="password.modify",
    ),
]
