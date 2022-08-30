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

from .views import (
    FieldsManageableViewSet,
    FieldsOrderViewSet,
    FieldsViewSet,
    FieldsVisibleViewSet,
    GeneralLogViewSet,
    LoginLogViewSet,
    SyncTaskLogViewSet,
    SyncTaskViewSet,
)

urlpatterns = [
    # sync task
    path(
        "api/v2/sync_task/",
        SyncTaskViewSet.as_view({"get": "list"}),
        name="sync_task.list",
    ),
    path("api/v2/sync_task/<task_id>/logs", SyncTaskLogViewSet.as_view({"get": "list"}), name="sync_task.show_logs"),
    # audit logs
    path("api/v2/audit/operation_logs/", GeneralLogViewSet.as_view({"get": "list"}), name="operation_logs"),
    path("api/v2/audit/login_log/", LoginLogViewSet.as_view({"get": "list"}), name="login_log"),
    # fields
    path("api/v2/fields/manageable/", FieldsManageableViewSet.as_view({"get": "get"}), name="fields.manageable"),
    path("api/v2/fields/visible/", FieldsVisibleViewSet.as_view({"patch": "patch"}), name="fields.visible"),
    path(
        "api/v2/fields/<int:id>/order/<int:order>/",
        FieldsOrderViewSet.as_view({"patch": "patch"}),
        name="fields.order",
    ),
    path("api/v2/fields/", FieldsViewSet.as_view({"get": "list", "post": "create"}), name="fields.list_create"),
    path(
        "api/v2/fields/<int:id>/",
        FieldsViewSet.as_view({"put": "update", "delete": "delete", "patch": "update"}),
        name="fields.list_create",
    ),
]
