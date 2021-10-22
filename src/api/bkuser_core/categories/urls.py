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
from bkuser_core.common.constants import LOOKUP_FIELD_NAME
from django.urls.conf import path, re_path

from . import views

PVAR_PROFILE_ID = r"(?P<%s>[a-z0-9-]+)" % LOOKUP_FIELD_NAME


urlpatterns = [
    re_path(
        r"^api/v2/categories_metas/$",
        views.CategoryViewSet.as_view(
            {
                "get": "list_metas",
            }
        ),
        name="categories.metas",
    ),
    re_path(
        r"^api/v2/categories/$",
        views.CategoryViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="categories",
    ),
    re_path(
        r"^api/v2/categories/%s/$" % PVAR_PROFILE_ID,
        views.CategoryViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="categories.action",
    ),
    re_path(
        r"^api/v2/categories/%s/restoration/$" % PVAR_PROFILE_ID,
        views.CategoryViewSet.as_view(
            {
                "post": "restoration",
            }
        ),
        name="categories.restoration",
    ),
    re_path(
        r"^api/v2/categories/%s/sync/$" % PVAR_PROFILE_ID,
        views.CategoryViewSet.as_view(
            {
                "post": "sync",
            }
        ),
        name="categories.sync",
    ),
    re_path(
        r"^api/v2/categories/%s/import/$" % PVAR_PROFILE_ID,
        views.CategoryFileViewSet.as_view(
            {
                "post": "import_data_file",
            }
        ),
        name="categories.import",
    ),
    re_path(
        r"^api/v2/categories/%s/test_connection/$" % PVAR_PROFILE_ID,
        views.CategoryViewSet.as_view(
            {
                "post": "test_connection",
            }
        ),
        name="categories.test_connection",
    ),
    re_path(
        r"^api/v2/categories/%s/test_fetch_data/$" % PVAR_PROFILE_ID,
        views.CategoryViewSet.as_view(
            {
                "post": "test_fetch_data",
            }
        ),
        name="categories.test_fetch_data",
    ),
    path("api/v2/sync_task/", views.SyncTaskViewSet.as_view({"get": "list"}), name="categories.sync_tasks"),
    path(
        "api/v2/sync_task/<lookup_value>/logs",
        views.SyncTaskViewSet.as_view({"get": "show_logs"}),
        name="categories.sync_tasks.logs",
    ),
]
