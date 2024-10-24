# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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

from django.urls import path

from . import views

urlpatterns = [
    # 查询目录列表
    path("categories/", views.CategoriesListApi.as_view(), name="open_v2.list_categories"),
    # 查询部门列表
    path("departments/", views.DepartmentListApi.as_view(), name="open_v2.list_departments"),
    # 查询单个部门信息
    path("departments/<str:id>/", views.DepartmentRetrieveApi.as_view(), name="open_v2.retrieve_department"),
    # 查询子部门列表
    path(
        "departments/<str:lookup_value>/children/",
        views.DepartmentChildrenListApi.as_view(),
        name="open_v2.list_department_children",
    ),
    # 查询单个用户的部门列表
    path(
        "profiles/<str:lookup_value>/departments/",
        views.ProfileDepartmentListApi.as_view(),
        name="open_v2.list_profile_departments",
    ),
    # 与上面 API 一样，只是兼容了缺少末尾 / 的情况 （ESB yaml 配置里是该情况）
    path(
        "profiles/<str:lookup_value>/departments",
        views.ProfileDepartmentListApi.as_view(),
        name="open_v2.list_profile_departments.without_slash",
    ),
    # 查询部门用户关系表
    path(
        "edges/department_profile/",
        views.DepartmentProfileRelationListApi.as_view(),
        name="open_v2.list_department_profile_relations",
    ),
    # 查询用户 Leader 关系表
    path(
        "edges/leader/",
        views.ProfileLeaderRelationListApi.as_view(),
        name="open_v2.list_profile_leader_relations",
    ),
    # 查询用户列表
    path("profiles/", views.ProfileListApi.as_view(), name="open_v2.list_profiles"),
    # 查询单个用户信息
    path("profiles/<str:lookup_value>/", views.ProfileRetrieveApi.as_view(), name="open_v2.retrieve_profile"),
    # 查询部门下用户列表
    path(
        "departments/<str:id>/profiles/",
        views.DepartmentProfileListApi.as_view(),
        name="open_v2.list_department_profiles",
    ),
    # 与上面 API 一样，只是兼容了缺少末尾 / 的情况 （ESB yaml 配置里是该情况）
    path(
        "departments/<str:id>/profiles",
        views.DepartmentProfileListApi.as_view(),
        name="open_v2.list_department_profiles.without_slash",
    ),
    # 更新用户语言
    path(
        "profiles/<str:username>/languages/",
        views.ProfileLanguageUpdateApi.as_view(),
        name="open_v2.update_profile_language",
    ),
]
