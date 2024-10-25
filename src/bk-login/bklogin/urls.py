# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
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
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path(
        # 兼容旧版本，与 PaaS V2 / Console 共享域名，/login 路径前缀指向登录服务
        "login/",
        include(
            [
                path("", include("bklogin.authentication.urls")),
                path("", include("bklogin.open_apis.urls")),
            ]
        ),
    ),
    path("", include("bklogin.monitoring.urls")),
]

# 蓝鲸通知中心
if settings.ENABLE_BK_NOTICE:
    urlpatterns += [
        path("/login/notices/", include(("bk_notice_sdk.urls", "notice"), namespace="notice")),
    ]
