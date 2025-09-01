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
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError

pytestmark = pytest.mark.django_db


class TestWeComAccessTokenApi:
    def test_get_access_token_with_cmsi(self, api_client):
        """测试从 CMSI 获取 access_token"""

        with (
            mock.patch("bkuser.biz.wecom.get_wecom_config") as mock_config,
            mock.patch("bkuser.biz.wecom.get_access_token_from_cmsi") as mock_cmsi,
        ):
            mock_config.return_value = {"corp_id": "test_corp_id", "corp_secret": "test_corp_secret"}
            mock_cmsi.return_value = "cmsi_access_token_456"

            resp = api_client.get(
                reverse("plugin.wecom.access_token"),
                data={"corp_id": "test_corp_id", "corp_secret": "test_corp_secret", "tenant_id": "test_tenant"},
            )

            assert resp.status_code == status.HTTP_200_OK

    def test_get_access_token_with_wecom_server_config(self, api_client):
        """测试从企业微信服务器获取 access_token"""
        with (
            mock.patch("bkuser.biz.wecom.get_wecom_config") as mock_config,
            mock.patch("bkuser.biz.wecom.WeComAccessTokenManager._fetch_access_token") as mock_fetch_access_token,
        ):
            mock_config.return_value = {"corp_id": "another_corp_id", "corp_secret": "another_corp_secret"}
            mock_fetch_access_token.return_value = ("wecom_access_token_789", 10)

            resp = api_client.get(
                reverse("plugin.wecom.access_token"),
                data={"corp_id": "test_corp_id", "corp_secret": "test_corp_secret", "tenant_id": "test_tenant"},
            )

            assert resp.status_code == status.HTTP_200_OK
            assert resp.data["access_token"] == "wecom_access_token_789"

    def test_get_access_token_with_invalid_params(self, api_client):
        """测试无效参数"""
        with mock.patch("bkuser.biz.wecom.WeComAccessTokenManager.get_access_token") as mock_get_access_token:
            mock_get_access_token.side_effect = ValidationError("Invalid corp_id or corp_secret")

            resp = api_client.get(
                reverse("plugin.wecom.access_token"),
                data={"corp_id": "invalid_corp_id", "corp_secret": "invalid_corp_secret", "tenant_id": "test_tenant"},
            )

            assert resp.status_code == status.HTTP_400_BAD_REQUEST
