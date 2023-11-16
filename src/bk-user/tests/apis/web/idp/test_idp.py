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
from typing import Any, Dict, List

import pytest
from bkuser.apps.data_source.models import DataSource
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from django.urls import reverse
from rest_framework import status

from tests.test_utils.helpers import generate_random_string

pytestmark = pytest.mark.django_db


@pytest.fixture()
def default_data_source(default_tenant) -> DataSource:
    default_data_source = DataSource.objects.filter(owner_tenant_id=default_tenant.id).first()
    assert default_tenant is not None
    return default_data_source


@pytest.fixture()
def wecom_plugin_cfg() -> Dict[str, Any]:
    """企业微信插件配置"""
    return {
        "corp_id": generate_random_string(),
        "agent_id": generate_random_string(),
        "secret": generate_random_string(),
    }


@pytest.fixture()
def data_source_match_rules(default_data_source) -> List[Dict[str, Any]]:
    """匹配数据源规则"""
    return [
        {
            "data_source_id": default_data_source.id,
            # Note: 当前只允许匹配内建字段
            "field_compare_rules": [{"source_field": "user_id", "target_field": "username"}],
        }
    ]


class TestIdpPluginListApi:
    def test_list(self, api_client):
        resp = api_client.get(reverse("idp_plugin.list"))
        # 至少有一个默认的本地账密认证源插件
        assert len(resp.data) >= 1
        assert BuiltinIdpPluginEnum.LOCAL in [i["id"] for i in resp.data]


class TestIdpCreateApi:
    def test_create_with_wecom_idp(self, api_client, wecom_plugin_cfg, data_source_match_rules):
        resp = api_client.post(
            reverse("idp.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": BuiltinIdpPluginEnum.WECOM,
                "plugin_config": wecom_plugin_cfg,
                "data_source_match_rules": data_source_match_rules,
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_with_not_exist_plugin(self, api_client):
        resp = api_client.post(
            reverse("idp.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": generate_random_string(),
                "plugin_config": {},
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "认证源插件不存在" in resp.data["message"]

    def test_create_with_not_allowed_local_idp(self, api_client):
        resp = api_client.post(
            reverse("idp.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": BuiltinIdpPluginEnum.LOCAL,
                "plugin_config": {},
                "data_source_match_rules": [],
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不允许创建本地账密认证源" in resp.data["message"]

    def test_create_with_invalid_plugin_config(self, api_client, data_source_match_rules):
        request_data = {
            "name": generate_random_string(),
            "plugin_id": BuiltinIdpPluginEnum.WECOM,
            "data_source_match_rules": data_source_match_rules,
            "plugin_config": {},
        }

        resp = api_client.post(reverse("idp.list_create"), data=request_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "认证源插件配置不合法" in resp.data["message"]

        request_data["plugin_config"] = {"corp_id": generate_random_string()}
        resp = api_client.post(reverse("idp.list_create"), data=request_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "认证源插件配置不合法" in resp.data["message"]

    def test_create_with_invalid_data_source_match_rule(self, api_client, wecom_plugin_cfg, default_data_source):
        request_data = {
            "name": generate_random_string(),
            "plugin_id": BuiltinIdpPluginEnum.WECOM,
            "plugin_config": wecom_plugin_cfg,
            "data_source_match_rules": [
                {
                    "data_source_id": 100000000000,
                    "field_compare_rules": [{"source_field": "user_id", "target_field": "username"}],
                }
            ],
        }

        resp = api_client.post(reverse("idp.list_create"), data=request_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "数据源必须是当前租户下的" in resp.data["message"]

        request_data["data_source_match_rules"] = [
            {
                "data_source_id": default_data_source.id,
                "field_compare_rules": [{"source_field": "user_id", "target_field": "not_builtin_field"}],
            }
        ]
        resp = api_client.post(reverse("idp.list_create"), data=request_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "当前仅支持匹配内置字段" in resp.data["message"]
