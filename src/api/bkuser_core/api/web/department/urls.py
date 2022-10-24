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
        views.DepartmentListCreateApi.as_view(),
        name="department.list_create",
    ),
    path(
        "<int:id>/",
        views.DepartmentRetrieveUpdateDeleteApi.as_view(),
        name="department.update_delete",
    ),
    path(
        "<int:id>/profiles/",
        views.DepartmentProfileListCreateApi.as_view(),
        name="department.profile.list",
    ),
    path(
        "<int:id>/operations/switch_order/<int:another_id>/",
        views.DepartmentOperationSwitchOrderApi.as_view(),
        name="department.operation.switch_order",
    ),
    # NOTE: replace of /api/v3/departments/
    path(
        "search/",
        views.DepartmentSearchApi.as_view(),
        name="department.search",
    ),
]
