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
from typing import Any, Dict

import pytest
from bkuser.apps.data_source.constants import DataSourcePluginEnum, DataSourceStatus
from bkuser.apps.data_source.models import DataSource, DataSourcePlugin
from bkuser.apps.data_source.plugins.local.constants import NotificationMethod, PasswordGenerateMethod
from django.urls import reverse
from rest_framework import status

from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import DEFAULT_TENANT

pytestmark = pytest.mark.django_db


@pytest.fixture()
def local_ds_plugin_config() -> Dict[str, Any]:
    return {
        "enable_login_by_password": True,
        "password_rule": {
            "min_length": 12,
            "contain_lowercase": True,
            "contain_uppercase": True,
            "contain_digit": True,
            "contain_punctuation": True,
            "not_continuous_count": 5,
            "not_keyboard_order": True,
            "not_continuous_letter": True,
            "not_continuous_digit": True,
            "not_repeated_symbol": True,
            "valid_time": 86400,
            "max_retries": 3,
            "lock_time": 3600,
        },
        "password_initial": {
            "force_change_at_first_login": True,
            "cannot_use_previous_password": True,
            "reserved_previous_password_count": 3,
            "generate_method": PasswordGenerateMethod.RANDOM,
            "fixed_password": None,
            "notification": {
                "methods": [NotificationMethod.EMAIL, NotificationMethod.SMS],
                "template": "你的密码是 xxx",
            },
        },
        "password_expire": {
            "remind_before_expire": [3600, 7200],
            "notification": {
                "methods": [NotificationMethod.EMAIL, NotificationMethod.SMS],
                "template": "密码即将过期,请尽快修改",
            },
        },
    }


@pytest.fixture()
def local_ds_plugin() -> DataSourcePlugin:
    return DataSourcePlugin.objects.get(id=DataSourcePluginEnum.LOCAL)


@pytest.fixture()
def data_source(request, local_ds_plugin, local_ds_plugin_config):
    # 支持检查是否使用 random_tenant fixture 以生成不属于默认租户的数据源
    tenant_id = DEFAULT_TENANT
    if "random_tenant" in request.fixturenames:
        tenant_id = request.getfixturevalue("random_tenant")

    return DataSource.objects.create(
        name=generate_random_string(),
        owner_tenant_id=tenant_id,
        plugin=local_ds_plugin,
        plugin_config=local_ds_plugin_config,
    )


class TestDataSourcePluginListApi:
    def test_list(self, api_client):
        resp = api_client.get(reverse("data_source_plugin.list"))
        # 至少会有一个本地数据源插件
        assert len(resp.data) >= 1
        assert DataSourcePluginEnum.LOCAL in [d["id"] for d in resp.data]


class TestDataSourceCreateApi:
    def test_create_local_data_source(self, api_client, local_ds_plugin_config):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": local_ds_plugin_config,
                # 本地数据源不需要字段映射配置
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_with_not_exist_plugin(self, api_client):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": "not_exist_plugin",
                "plugin_config": {},
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "数据源插件不存在" in resp.data["message"]

    def test_create_without_plugin_config(self, api_client):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={"name": generate_random_string(), "plugin_id": DataSourcePluginEnum.LOCAL},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "plugin_config: 该字段是必填项。" in resp.data["message"]

    def test_create_with_invalid_plugin_config(self, api_client, local_ds_plugin_config):
        local_ds_plugin_config.pop("enable_login_by_password")
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": local_ds_plugin_config,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "插件配置不合法：enable_login_by_password: Field required" in resp.data["message"]

    def test_create_without_required_field_mapping(self, api_client):
        """非本地数据源，需要字段映射配置"""
        # TODO 需要内置非本地的数据源插件后补全测试用例


class TestDataSourceListApi:
    def test_list(self, api_client, data_source):
        resp = api_client.get(reverse("data_source.list_create"))
        assert len(resp.data) != 0

    def test_list_with_keyword(self, api_client, data_source):
        resp = api_client.get(reverse("data_source.list_create"), data={"keyword": data_source.name})
        assert len(resp.data) == 1

        ds = resp.data[0]
        assert ds["id"] == data_source.id
        assert ds["name"] == data_source.name
        assert ds["owner_tenant_id"] == data_source.owner_tenant_id
        assert ds["plugin_name"] == DataSourcePluginEnum.get_choice_label(DataSourcePluginEnum.LOCAL)
        assert ds["status"] == DataSourceStatus.ENABLED
        assert ds["collaborative_companies"] == []

    def test_list_other_tenant_data_source(self, api_client, random_tenant, data_source):
        resp = api_client.get(reverse("data_source.list_create"), data={"keyword": data_source.name})
        # 无法查看到其他租户的数据源信息
        assert len(resp.data) == 0


class TestDataSourceUpdateApi:
    def test_update_local_data_source(self, api_client, data_source, local_ds_plugin_config):
        local_ds_plugin_config["enable_login_by_password"] = False
        resp = api_client.put(
            reverse("data_source.retrieve_update", kwargs={"id": data_source.id}),
            data={"plugin_config": local_ds_plugin_config},
        )
        assert resp.status_code == status.HTTP_200_OK

        resp = api_client.get(reverse("data_source.retrieve_update", kwargs={"id": data_source.id}))
        assert resp.data["plugin_config"]["enable_login_by_password"] is False

    def test_update_with_invalid_plugin_config(self, api_client, data_source, local_ds_plugin_config):
        local_ds_plugin_config.pop("enable_login_by_password")
        resp = api_client.put(
            reverse("data_source.retrieve_update", kwargs={"id": data_source.id}),
            data={"plugin_config": local_ds_plugin_config},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "插件配置不合法：enable_login_by_password: Field required" in resp.data["message"]

    def test_update_without_required_field_mapping(self, api_client):
        """非本地数据源，需要字段映射配置"""
        # TODO 需要内置非本地的数据源插件后补全测试用例


class TestDataSourceRetrieveApi:
    def test_retrieve(self, api_client, data_source):
        resp = api_client.get(reverse("data_source.retrieve_update", kwargs={"id": data_source.id}))
        assert resp.data["id"] == data_source.id
        assert resp.data["name"] == data_source.name
        assert resp.data["owner_tenant_id"] == data_source.owner_tenant_id
        assert resp.data["plugin"]["id"] == DataSourcePluginEnum.LOCAL
        assert resp.data["plugin"]["name"] == DataSourcePluginEnum.get_choice_label(DataSourcePluginEnum.LOCAL)
        assert resp.data["status"] == DataSourceStatus.ENABLED
        assert resp.data["plugin_config"] == data_source.plugin_config
        assert resp.data["sync_config"] == data_source.sync_config
        assert resp.data["field_mapping"] == data_source.field_mapping

    def test_retrieve_other_tenant_data_source(self, api_client, random_tenant, data_source):
        resp = api_client.get(reverse("data_source.retrieve_update", kwargs={"id": data_source.id}))
        # 无法查看到其他租户的数据源信息
        assert resp.status_code == status.HTTP_404_NOT_FOUND