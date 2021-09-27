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

from .views import GeneralLogViewSet, LoginLogViewSet

urlpatterns = [
    ##############
    # audit_logs #
    ##############
    path("api/v2/audit/operation_logs/", GeneralLogViewSet.as_view({"get": "list"}), name="operation_logs"),
    path("api/v2/audit/login_log/", LoginLogViewSet.as_view({"get": "list"}), name="login_log"),
    path("api/v2/audit/login_log/export/", LoginLogViewSet.as_view({"get": "export"}), name="export_login_log"),
]
