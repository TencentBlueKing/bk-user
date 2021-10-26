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
from django.conf.urls import url

from . import views

PVAR_CATEGORIES_ID = r"(?P<category_id>[0-9]+)"
PVAR_ANOTHER_CATEGORIES_ID = r"(?P<another_category_id>[a-z0-9-]+)"


urlpatterns = [
    ##############
    # categories #
    ##############
    url(
        r"^api/v2/categories_metas/$",
        views.CategoriesViewSet.as_view(
            {
                "get": "list_metas",
            }
        ),
        name="categories.metas",
    ),
    url(
        r"^api/v2/categories/$",
        views.CategoriesViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="categories",
    ),
    url(
        r"^api/v2/categories/default/$",
        views.CategoriesViewSet.as_view(
            {
                "get": "get_default",
            }
        ),
        name="categories.default",
    ),
    url(
        r"^api/v2/categories/%s/$" % PVAR_CATEGORIES_ID,
        views.CategoriesViewSet.as_view(
            {
                "patch": "update",
                "delete": "delete",
            }
        ),
        name="categories.actions",
    ),
    url(
        r"^api/v2/categories/%s/switch_order/%s/$" % (PVAR_CATEGORIES_ID, PVAR_ANOTHER_CATEGORIES_ID),
        views.CategoriesViewSet.as_view(
            {
                "patch": "switch_order",
            }
        ),
        name="categories.switch_order",
    ),
    url(
        r"^api/v2/categories/%s/sync/$" % PVAR_CATEGORIES_ID,
        views.CategoriesSyncViewSet.as_view(
            {
                "post": "sync",
            }
        ),
        name="categories.sync",
    ),
    url(
        r"^api/v2/categories/%s/activate/$" % PVAR_CATEGORIES_ID,
        views.CategoriesSyncViewSet.as_view(
            {
                "post": "activate",
            }
        ),
        name="categories.activate",
    ),
    url(
        r"^api/v2/categories/%s/test_connection/$" % PVAR_CATEGORIES_ID,
        views.CategoriesSyncViewSet.as_view(
            {
                "post": "test_connection",
            }
        ),
        name="categories.test_connection",
    ),
    url(
        r"^api/v2/categories/%s/test_fetch_data/$" % PVAR_CATEGORIES_ID,
        views.CategoriesSyncViewSet.as_view(
            {
                "post": "test_fetch_data",
            }
        ),
        name="categories.test_fetch_data",
    ),
    url(
        r"^api/v2/categories/%s/export/$" % PVAR_CATEGORIES_ID,
        views.CategoriesExportViewSet.as_view(
            {
                "get": "export",
            }
        ),
        name="categories.export",
    ),
    url(
        r"^api/v2/categories/%s/export_template/$" % PVAR_CATEGORIES_ID,
        views.CategoriesExportViewSet.as_view(
            {
                "get": "export_template",
            }
        ),
        name="categories.export_template",
    ),
]
