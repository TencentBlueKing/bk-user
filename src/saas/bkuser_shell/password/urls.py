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
from django.conf.urls import url

from .views import PasswordViewSet

urlpatterns = [
    ############
    # password #
    ############
    url(
        r"^api/v1/password/reset/$",
        PasswordViewSet.as_view(
            {
                "post": "reset",
            }
        ),
        name="password.reset",
    ),
    url(
        r"^api/v1/password/reset_by_token/$",
        PasswordViewSet.as_view(
            {
                "post": "reset_by_token",
            }
        ),
        name="password.reset_by_token",
    ),
    url(
        r"^api/v1/password/modify/$",
        PasswordViewSet.as_view(
            {
                "post": "modify",
            }
        ),
        name="password.modify",
    ),
]
