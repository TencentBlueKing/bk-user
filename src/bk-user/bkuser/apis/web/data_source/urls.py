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
from django.urls import path

from bkuser.apis.web.data_source import views

urlpatterns = [
    # 数据源插件列表
    path("plugins/", views.DataSourcePluginListApi.as_view(), name="data_source_plugin.list"),
    # 数据源创建/获取列表
    path("", views.DataSourceListCreateApi.as_view(), name="data_source.list_create"),
    # 数据源更新/获取
    path("<int:id>/", views.DataSourceRetrieveUpdateApi.as_view(), name="data_source.retrieve_update"),
    # 通用数据源连通性测试
    path(
        "<int:id>/connectivity/",
        views.DataSourceConnectivityApi.as_view(),
        name="data_source.connectivity_test",
    ),
    # 数据源用户
    path("<int:id>/users/", views.DataSourceUserListCreateApi.as_view(), name="data_source_user.list_create"),
    # 本地数据源用户导入导出
    path("<int:id>/users/io/", views.DataSourceUserImportExportApi.as_view(), name="data_source_user.import_export"),
    # 数据源用户 Leader
    path("<int:id>/leaders/", views.DataSourceLeadersListApi.as_view(), name="data_source_leaders.list"),
    # 数据源部门
    path("<int:id>/departments/", views.DataSourceDepartmentsListApi.as_view(), name="data_source_departments.list"),
]
