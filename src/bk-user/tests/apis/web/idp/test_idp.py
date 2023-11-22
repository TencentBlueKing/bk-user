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
from bkuser.apps.idp.models import Idp, IdpPlugin
from bkuser.common.constants import SENSITIVE_MASK
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.idp_plugins.wecom.plugin import WecomIdpPluginConfig
from django.urls import reverse
from rest_framework import status

from tests.test_utils.helpers import generate_random_string

pytestmark = pytest.mark.django_db


@pytest.fixture()
def default_data_source(default_tenant) -> DataSource:
    default_data_source = DataSource.objects.filter(owner_tenant_id=default_tenant.id).first()
    assert default_data_source is not None
    return default_data_source


@pytest.fixture()
def default_idp(default_tenant) -> Idp:
    default_idp = Idp.objects.filter(owner_tenant_id=default_tenant.id).first()
    assert default_idp is not None
    return default_idp


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


@pytest.fixture()
def wecom_idp(bk_user, default_tenant, wecom_plugin_cfg, data_source_match_rules) -> Idp:
    return Idp.objects.create(
        name=generate_random_string(),
        owner_tenant_id=default_tenant.id,
        plugin=IdpPlugin.objects.get(id=BuiltinIdpPluginEnum.WECOM),
        plugin_config=WecomIdpPluginConfig(**wecom_plugin_cfg),
        data_source_match_rules=data_source_match_rules,
        creator=bk_user.username,
        updater=bk_user.username,
    )


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

    def test_create_with_invalid_data_source_match_rules(self, api_client, wecom_plugin_cfg, default_data_source):
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
                "field_compare_rules": [{"source_field": "user_id", "target_field": generate_random_string()}],
            }
        ]
        resp = api_client.post(reverse("idp.list_create"), data=request_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不属于用户自定义字段或内置字段" in resp.data["message"]

    def test_create_with_empty_data_source_match_rules(self, api_client, wecom_plugin_cfg, default_data_source):
        request_data = {
            "name": generate_random_string(),
            "plugin_id": BuiltinIdpPluginEnum.WECOM,
            "plugin_config": wecom_plugin_cfg,
            "data_source_match_rules": [],
        }
        resp = api_client.post(reverse("idp.list_create"), data=request_data)
        assert resp.status_code == status.HTTP_201_CREATED


class TestIdpListApi:
    def test_list(self, api_client, default_idp):
        resp = api_client.get(reverse("idp.list_create"))
        assert len(resp.data) != 0

        resp = api_client.get(reverse("idp.list_create"), data={"keyword": default_idp.name})
        assert len(resp.data) == 1

        idp = resp.data[0]
        assert idp["id"] == default_idp.id


class TestIdpUpdateApi:
    def test_update_with_wecom_idp(self, api_client, wecom_idp):
        new_name = generate_random_string()
        new_plugin_config = {
            "corp_id": generate_random_string(),
            "agent_id": generate_random_string(),
            "secret": generate_random_string(),
        }
        resp = api_client.put(
            reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}),
            data={
                "name": new_name,
                "plugin_config": new_plugin_config,
                "data_source_match_rules": [],
            },
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        idp = Idp.objects.get(id=wecom_idp.id)
        assert idp.name == new_name
        assert len(idp.data_source_match_rules) == 0
        assert idp.plugin_config["corp_id"] == new_plugin_config["corp_id"]
        assert idp.plugin_config["agent_id"] == new_plugin_config["agent_id"]
        assert idp.plugin_config["secret"] == SENSITIVE_MASK
        assert idp.get_plugin_cfg().model_dump() == new_plugin_config

    def test_update_with_invalid_plugin_config(self, api_client, wecom_idp):
        resp = api_client.put(
            reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}),
            data={
                "name": wecom_idp.name,
                "plugin_config": {},
                "data_source_match_rules": wecom_idp.data_source_match_rules,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "认证源插件配置不合法" in resp.data["message"]

        resp = api_client.put(
            reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}),
            data={
                "name": wecom_idp.name,
                "plugin_config": {"corp_id": generate_random_string()},
                "data_source_match_rules": wecom_idp.data_source_match_rules,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "认证源插件配置不合法" in resp.data["message"]

    def test_partial_update_with_name(self, api_client, wecom_idp):
        new_name = generate_random_string()
        resp = api_client.patch(
            reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}),
            data={"name": new_name, "data_source_match_rules": []},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        idp = Idp.objects.get(id=wecom_idp.id)
        assert idp.name == new_name
        assert len(idp.data_source_match_rules) == len(wecom_idp.data_source_match_rules)

    def test_partial_update_with_duplicate_name(self, bk_user, api_client, wecom_idp):
        new_name = generate_random_string()
        Idp.objects.create(
            name=new_name,
            owner_tenant_id=wecom_idp.owner_tenant_id,
            plugin=wecom_idp.plugin,
            plugin_config=WecomIdpPluginConfig(**wecom_idp.plugin_config),
            data_source_match_rules=wecom_idp.data_source_match_rules,
            creator=bk_user.username,
            updater=bk_user.username,
        )
        resp = api_client.patch(reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}), data={"name": new_name})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "同名认证源已存在" in resp.data["message"]


class TestIdpRetrieveApi:
    def test_retrieve(self, api_client, wecom_idp):
        resp = api_client.get(reverse("idp.retrieve_update", kwargs={"id": wecom_idp.id}))
        assert resp.data["id"] == wecom_idp.id
        assert resp.data["name"] == wecom_idp.name
        assert resp.data["owner_tenant_id"] == wecom_idp.owner_tenant_id
        assert resp.data["status"] == wecom_idp.status
        assert resp.data["plugin"]["id"] == wecom_idp.plugin.id
        assert resp.data["plugin"]["name"] == wecom_idp.plugin.name
        assert resp.data["plugin_config"] == wecom_idp.plugin_config
        assert resp.data["data_source_match_rules"] == wecom_idp.data_source_match_rules
        assert resp.data["callback_uri"] == wecom_idp.callback_uri
