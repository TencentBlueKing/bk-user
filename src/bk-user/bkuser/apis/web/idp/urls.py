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

from . import views

urlpatterns = [
    # 认证源插件列表
    path("plugins/", views.IdpPluginListApi.as_view(), name="idp_plugin.list"),
    # 认证源插件配置元数据
    path(
        "plugins/<str:id>/config-meta/",
        views.IdpPluginConfigMetaRetrieveApi.as_view(),
        name="idp_plugin_config_meta.retrieve",
    ),
    # 认证源创建/获取列表
    path("", views.IdpListCreateApi.as_view(), name="idp.list_create"),
    # 认证源获取/更新
    path("<str:id>/", views.IdpRetrieveUpdateApi.as_view(), name="idp.retrieve_update"),
]
