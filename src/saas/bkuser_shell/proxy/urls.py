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
    CategoriesSyncViewSet,
    CategoriesTestConnectionViewSet,
    CategoriesTestFetchDataViewSet,
    CategoryListCreateViewSet,
    CategoryMetasViewSet,
    CategoryUpdateDeleteViewSet,
    DepartmentSearchViewSet,
    FieldsManageableViewSet,
    FieldsOrderViewSet,
    FieldsViewSet,
    FieldsVisibleViewSet,
    GeneralLogViewSet,
    HealthzViewSet,
    LoginInfoViewSet,
    LoginLogViewSet,
    ProfilesSearchViewSet,
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
        "api/v2/categories/<int:id>/sync/",
        CategoriesSyncViewSet.as_view({"post": "post"}),
        name="categories.sync",
    ),
    # settings
    path("api/v2/settings/metas/", SettingsMetasViewSet.as_view({"get": "get"}), name="settings.metas"),
    # departments
    path("api/v3/departments/", DepartmentSearchViewSet.as_view({"get": "get"}), name="departments.search"),
    path("api/v3/profiles/", ProfilesSearchViewSet.as_view({"get": "get"}), name="profiles.search"),
]
