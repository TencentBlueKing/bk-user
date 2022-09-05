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
        views.CategoryUpdateApi.as_view(),
        name="category.update",
    ),
    path(
        "<int:id>/settings/",
        views.CategorySettingListApi.as_view(),
        name="category.setting.list",
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
        "metas/",
        views.CategoryMetasListApi.as_view(),
        name="category.metas",
    ),
]

# 目录修改order
# /api/v2/categories/2/switch_order/1/
