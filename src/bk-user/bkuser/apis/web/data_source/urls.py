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
    # 数据源插件默认配置
    path(
        "plugins/<str:id>/default-config/",
        views.DataSourcePluginDefaultConfigApi.as_view(),
        name="data_source_plugin.default_config",
    ),
    # 数据源创建/获取列表
    path("", views.DataSourceListCreateApi.as_view(), name="data_source.list_create"),
    # 数据源随机密码获取
    path("random-passwords/", views.DataSourceRandomPasswordApi.as_view(), name="data_source.random_passwords"),
    # 数据源连通性测试
    path(
        "test-connection/",
        views.DataSourceTestConnectionApi.as_view(),
        name="data_source.test_connection",
    ),
    # 数据源同步记录
    path(
        "sync-records/",
        views.DataSourceSyncRecordListApi.as_view(),
        name="data_source.sync_record.list",
    ),
    # 数据源同步记录日志详情
    path(
        "sync-records/<int:id>/",
        views.DataSourceSyncRecordRetrieveApi.as_view(),
        name="data_source.sync_record.retrieve",
    ),
    # 数据源更新/获取
    path("<int:id>/", views.DataSourceRetrieveUpdateApi.as_view(), name="data_source.retrieve_update"),
    # 数据源启/停
    path(
        "<int:id>/operations/switch_status/",
        views.DataSourceSwitchStatusApi.as_view(),
        name="data_source.switch_status",
    ),
    # 获取用户信息导入模板
    path(
        "<int:id>/operations/download_template/",
        views.DataSourceTemplateApi.as_view(),
        name="data_source.download_template",
    ),
    # 导出数据源用户数据
    path("<int:id>/operations/export/", views.DataSourceExportApi.as_view(), name="data_source.export_data"),
    # 数据源导入
    path("<int:id>/operations/import/", views.DataSourceImportApi.as_view(), name="data_source.import_from_excel"),
    # 手动触发数据源同步
    path("<int:id>/operations/sync/", views.DataSourceSyncApi.as_view(), name="data_source.sync"),
]
