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
from unittest import mock

import pytest
from bklogin.authentication.manager import BkTokenManager
from bklogin.component.bk_user.models import TenantUserDetailInfo
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.fixture
def bk_token() -> str:
    bk_token, _ = BkTokenManager().generate("test_username")

    return bk_token


class TestTokenIntrospect:
    @pytest.fixture(autouse=True)
    def _mock_bk_user_component(self):
        with mock.patch(
            "bklogin.component.bk_user.api.get_tenant_user",
            return_value=TenantUserDetailInfo(
                id="test_username",
                username="test_username",
                full_name="test_fullname",
                display_name="test_display_name",
                tenant_id="test_tenant_id",
                data_source_type="real",
                language="zh-CN",
                time_zone="Asia/Shanghai",
            ),
        ):
            yield

    def test_standard(self, open_api_client, bk_token):
        resp = open_api_client.get(reverse("v3_open.bk_token.verify"), data={"bk_token": bk_token})

        assert resp.status_code == 200

        data = resp.json()["data"]
        assert data["bk_username"] == "test_username"
        assert data["tenant_id"] == "test_tenant_id"

    def test_invalid(self, open_api_client, bk_token):
        resp = open_api_client.get(reverse("v3_open.bk_token.verify"), data={"bk_token": f"invalid_{bk_token}"})

        assert resp.status_code == 400

    def test_userinfo_standard(self, open_api_client, bk_token):
        resp = open_api_client.get(reverse("v3_open.bk_token.userinfo_retrieve"), data={"bk_token": bk_token})

        assert resp.status_code == 200

        data = resp.json()["data"]
        assert data["bk_username"] == "test_username"
        assert data["tenant_id"] == "test_tenant_id"
        assert data["display_name"] == "test_display_name"
        assert data["language"] == "zh-CN"
        assert data["time_zone"] == "Asia/Shanghai"

    def test_userinfo_invalid(self, open_api_client, bk_token):
        resp = open_api_client.get(
            reverse("v3_open.bk_token.userinfo_retrieve"), data={"bk_token": f"invalid_{bk_token}"}
        )

        assert resp.status_code == 400
