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
from bkuser_core.common.constants import LOOKUP_FIELD_NAME
from django.conf.urls import url

from . import views

PVAR_PROFILE_ID = r"(?P<%s>[a-z0-9-]+)" % LOOKUP_FIELD_NAME

urlpatterns = [
    url(
        r"^api/v2/audit/general_log/$",
        views.GeneralLogViewSet.as_view({"get": "list"}),
        name="general_log",
    ),
    url(
        r"^api/v2/audit/general_log/%s/$" % PVAR_PROFILE_ID,
        views.GeneralLogViewSet.as_view({"get": "retrieve"}),
        name="general_log.action",
    ),
    url(
        r"^api/v2/audit/login_log/$",
        views.LoginLogViewSet.as_view({"get": "list"}),
        name="login_log",
    ),
    url(
        r"^api/v2/audit/login_log/%s/$" % PVAR_PROFILE_ID,
        views.LoginLogViewSet.as_view({"get": "retrieve"}),
        name="login_log.action",
    ),
    url(
        r"^api/v2/audit/reset_password_log/$",
        views.ResetPasswordLogViewSet.as_view({"get": "list"}),
        name="reset_password_log",
    ),
    url(
        r"^api/v2/audit/reset_password_log/%s/$" % PVAR_PROFILE_ID,
        views.ResetPasswordLogViewSet.as_view({"get": "retrieve"}),
        name="reset_password_log.action",
    ),
]
