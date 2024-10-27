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

import pytest
from bkuser.plugins.constants import DataSourcePluginEnum
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


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
        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestDataSourcePluginConfigMetaRetrieveApi:
    def test_retrieve_with_local_data_source_plugin(self, api_client):
        resp = api_client.get(
            reverse("data_source_plugin.config_meta.retrieve", args=[DataSourcePluginEnum.LOCAL.value])
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["json_schema"] != ""

    def test_retrieve_with_general_data_source_plugin(self, api_client):
        resp = api_client.get(
            reverse("data_source_plugin.config_meta.retrieve", args=[DataSourcePluginEnum.GENERAL.value])
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["json_schema"] != ""

    def test_retrieve_with_not_exists_data_source_plugin(self, api_client):
        resp = api_client.get(reverse("data_source_plugin.config_meta.retrieve", args=["not_exists"]))
        assert resp.status_code == status.HTTP_404_NOT_FOUND
