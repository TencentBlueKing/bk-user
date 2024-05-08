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
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.plugins.constants import DataSourcePluginEnum
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestCurrentTenantRetrieveApi:
    def test_standard(self, api_client, random_tenant, bare_local_data_source):
        resp = api_client.get(reverse("organization.tenant.retrieve"))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data.keys() == {"id", "name", "logo", "data_source"}

        assert resp.data["id"] == random_tenant.id
        assert resp.data["name"] == random_tenant.name

        data_source = resp.data["data_source"]
        assert data_source["id"] == bare_local_data_source.id
        assert data_source["type"] == DataSourceTypeEnum.REAL
        assert data_source["plugin_id"] == DataSourcePluginEnum.LOCAL


class TestCollaborationTenantListApi:
    @pytest.mark.usefixtures("_init_collaboration_users_depts")
    def test_standard(self, api_client, collaboration_tenant):
        resp = api_client.get(reverse("organization.collaboration_tenant.list"))

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1

        first_tenant = resp.data[0]
        assert first_tenant.keys() == {"id", "name", "logo"}
        assert first_tenant["id"] == collaboration_tenant.id
        assert first_tenant["name"] == collaboration_tenant.name
