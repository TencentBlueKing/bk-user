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

from . import views

urlpatterns = [
    path(
        "",
        views.CategoryListCreateApi.as_view(),
        name="category.list_create",
    ),
    path(
        "<int:id>/",
        views.CategoryUpdateDeleteApi.as_view(),
        name="category.update",
    ),
    path(
        "<int:id>/departments/",
        views.CategoryDepartmentListApi.as_view(),
        name="category.department.list",
    ),
    path(
        "<int:id>/profiles/",
        views.CategoryProfileListApi.as_view(),
        name="category.profile.list",
    ),
    path(
        "<int:id>/settings/namespaces/<str:namespace>/",
        views.CategorySettingNamespaceListCreateUpdateApi.as_view(),
        name="category.setting.namespace.list_update",
    ),
    path(
        "<int:id>/operations/test_fetch_data/",
        views.CategoryOperationTestFetchDataApi.as_view(),
        name="category.operation.test_fetch_data",
    ),
    path(
        "<int:id>/operations/test_connection/",
        views.CategoryOperationTestConnectionApi.as_view(),
        name="category.operation.test_connection",
    ),
    path(
        "<int:id>/operations/export_template/",
        views.CategoryOperationExportTemplateApi.as_view(),
        name="category.operation.export_template",
    ),
    path(
        "<int:id>/operations/export/",
        views.CategoryOperationExportApi.as_view(),
        name="category.operation.export",
    ),
    path(
        "<int:id>/operations/sync_or_import/",
        views.CategoryOperationSyncOrImportApi.as_view(),
        name="category.operation.sync_or_import",
    ),
    path(
        "<int:id>/operations/switch_order/<int:another_id>/",
        views.CategoryOperationSwitchOrderApi.as_view(),
        name="category.operation.switch_order",
    ),
    path(
        "metas/",
        views.CategoryMetasListApi.as_view(),
        name="category.metas",
    ),
]
