# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
import pytest
from bklogin.idp_plugins.http import HttpStatusCode
from bklogin.idp_plugins.local import client as local_client
from django.test import override_settings
from requests.auth import HTTPBasicAuth


@pytest.fixture
def captured_posts(monkeypatch):
    calls = []

    def fake_post(url, **kwargs):
        calls.append({"url": url, **kwargs})
        return HttpStatusCode(200), {"data": [{"id": "admin"}]}

    monkeypatch.setattr(local_client, "http_post", fake_post)
    return calls


@override_settings(
    BK_USER_APP_CODE="settings-user-code",
    BK_USER_APP_SECRET="settings-user-secret",
    BK_USER_API_URL="http://bk-user.settings",
)
def test_client_reads_credentials_from_django_settings(monkeypatch, captured_posts):
    monkeypatch.setenv("BK_USER_APP_CODE", "env-user-code")
    monkeypatch.setenv("BK_USER_APP_SECRET", "env-user-secret")
    monkeypatch.setenv("BK_USER_API_URL", "http://bk-user.env")

    users = local_client.BkUserAPIClient().auth_credentials_of_local_user([1], "admin", "password")

    assert users == [{"id": "admin"}]
    (call,) = captured_posts
    assert call["url"] == "http://bk-user.settings/api/v3/login/local-user-credentials/authenticate/"
    assert call["auth"] == HTTPBasicAuth("settings-user-code", "settings-user-secret")
