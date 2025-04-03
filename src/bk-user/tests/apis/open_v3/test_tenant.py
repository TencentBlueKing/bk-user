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
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestTenantListApi:
    def test_standard(self, api_client, default_tenant, random_tenant):
        resp = api_client.get(reverse("open_v3.tenant.list"))
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["id"] for t in resp.data} == {default_tenant.id, random_tenant.id}
        assert set(resp.data[0].keys()) == {"id", "name", "status"}


class TestTenantPropertyLookupApi:
    def test_standard(self, api_client, tenant_property):
        resp = api_client.get(reverse("open_v3.tenant_property.lookup"), data={"lookups": "key_1,key_2"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["key"] for t in resp.data} == {"key_1", "key_2"}
        assert {t["value"] for t in resp.data} == {"value_1", "value_2"}

    def test_with_not_match(self, api_client, tenant_property):
        resp = api_client.get(reverse("open_v3.tenant_property.lookup"), data={"lookups": "not_exist_1,not_exist_2"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0
