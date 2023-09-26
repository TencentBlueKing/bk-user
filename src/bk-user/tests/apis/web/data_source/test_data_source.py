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

import pytest
from bkuser.apps.data_source.constants import DataSourceStatus
from bkuser.apps.data_source.models import DataSource
from bkuser.plugins.constants import DataSourcePluginEnum
from django.urls import reverse
from rest_framework import status

from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import DEFAULT_TENANT

pytestmark = pytest.mark.django_db


@pytest.fixture()
def data_source(request, local_ds_plugin, local_ds_plugin_config):
    # 支持检查是否使用 random_tenant fixture 以生成不属于默认租户的数据源
    tenant_id = DEFAULT_TENANT
    if "random_tenant" in request.fixturenames:
        tenant_id = request.getfixturevalue("random_tenant").id

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


class TestDataSourcePluginDefaultConfigApi:
    def test_retrieve(self, api_client):
        resp = api_client.get(reverse("data_source_plugin.default_config", args=[DataSourcePluginEnum.LOCAL.value]))
        assert resp.status_code == status.HTTP_200_OK

    def test_retrieve_not_exists(self, api_client):
        resp = api_client.get(reverse("data_source_plugin.default_config", args=["not_exists"]))
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


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

    def test_create_with_minimal_plugin_config(self, api_client):
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": {"enable_account_password_login": False},
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

    def test_create_with_broken_plugin_config(self, api_client, local_ds_plugin_config):
        local_ds_plugin_config["password_initial"] = None
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": local_ds_plugin_config,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "密码生成规则、初始密码设置、密码到期设置均不能为空" in resp.data["message"]

    def test_create_with_invalid_notification_template(self, api_client, local_ds_plugin_config):
        local_ds_plugin_config["password_expire"]["notification"]["templates"][0]["title"] = None
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": local_ds_plugin_config,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "邮件通知模板需要提供标题" in resp.data["message"]

    def test_create_with_invalid_plugin_config(self, api_client, local_ds_plugin_config):
        local_ds_plugin_config.pop("enable_account_password_login")
        resp = api_client.post(
            reverse("data_source.list_create"),
            data={
                "name": generate_random_string(),
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": local_ds_plugin_config,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "插件配置不合法：enable_account_password_login: Field required" in resp.data["message"]

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
        assert ds["cooperation_tenants"] == []

    def test_list_other_tenant_data_source(self, api_client, random_tenant, data_source):
        resp = api_client.get(reverse("data_source.list_create"), data={"keyword": data_source.name})
        # 无法查看到其他租户的数据源信息
        assert len(resp.data) == 0


class TestDataSourceUpdateApi:
    def test_update_local_data_source(self, api_client, data_source, local_ds_plugin_config):
        local_ds_plugin_config["enable_account_password_login"] = False
        resp = api_client.put(
            reverse("data_source.retrieve_update", kwargs={"id": data_source.id}),
            data={"plugin_config": local_ds_plugin_config},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        resp = api_client.get(reverse("data_source.retrieve_update", kwargs={"id": data_source.id}))
        assert resp.data["plugin_config"]["enable_account_password_login"] is False

    def test_update_with_invalid_plugin_config(self, api_client, data_source, local_ds_plugin_config):
        local_ds_plugin_config.pop("enable_account_password_login")
        resp = api_client.put(
            reverse("data_source.retrieve_update", kwargs={"id": data_source.id}),
            data={"plugin_config": local_ds_plugin_config},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "插件配置不合法：enable_account_password_login: Field required" in resp.data["message"]

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


class TestDataSourceSwitchStatusApi:
    def test_switch(self, api_client, data_source):
        url = reverse("data_source.switch_status", kwargs={"id": data_source.id})
        # 默认启用，切换后不可用
        assert api_client.patch(url).data["status"] == DataSourceStatus.DISABLED
        # 再次切换，变成可用
        assert api_client.patch(url).data["status"] == DataSourceStatus.ENABLED

    def test_patch_other_tenant_data_source(self, api_client, random_tenant, data_source):
        resp = api_client.patch(reverse("data_source.switch_status", kwargs={"id": data_source.id}))
        # 无法操作其他租户的数据源信息
        assert resp.status_code == status.HTTP_404_NOT_FOUND
