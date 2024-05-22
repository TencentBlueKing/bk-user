# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.urls import include, path

from . import views

urlpatterns = [
    # 租户管理
    path(
        "tenants/",
        include(
            [
                path("", views.TenantListCreateApi.as_view(), name="tenant.list_create"),
                path(
                    "<str:id>/", views.TenantRetrieveUpdateDestroyApi.as_view(), name="tenant.retrieve_update_destroy"
                ),
                path("<str:id>/status/", views.TenantStatusUpdateApi.as_view(), name="tenant.update_status"),
                path(
                    "<str:id>/builtin-manager/",
                    views.TenantBuiltinManagerRetrieveUpdateApi.as_view(),
                    name="tenant.retrieve_update_builtin_manager",
                ),
                path(
                    "<str:id>/related-resource-statistics/",
                    views.TenantRelatedResourceStatsApi.as_view(),
                    name="tenant.related_resource_stats",
                ),
            ]
        ),
    ),
]
