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
from bkuser_shell.version_log import views
from django.conf.urls import url

VERSION_NUMBER = r"(?P<version_number>(\d+\.){1,3}(\d+))"

urlpatterns = [
    ##############
    # version_log #
    ##############
    url(
        r"^api/v2/version_logs_list/$",
        views.VersionLogViewSet.as_view(
            {"get": "list"},
        ),
        name="version_log_list",
    ),
    url(
        r"^api/v2/version_logs_list/%s/$" % VERSION_NUMBER,
        views.VersionLogViewSet.as_view(
            {"get": "retrieve"},
        ),
        name="version_log_detail",
    ),
]
