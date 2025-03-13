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


class TestDataSourceOwnerTenantListApi:
    def test_with_current_tenant(self, api_client, random_tenant):
        resp = api_client.get(reverse("open_web.data_source_owner_tenant.list"))

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["id"] == random_tenant.id
        assert resp.data[0]["name"] == random_tenant.name

    @pytest.mark.usefixtures("_init_collaboration_users_depts")
    def test_with_collaboration_tenants(self, api_client, random_tenant, collaboration_tenant):
        resp = api_client.get(reverse("open_web.data_source_owner_tenant.list"))

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 2
        assert {t["id"] for t in resp.data} == {random_tenant.id, collaboration_tenant.id}
        assert {t["name"] for t in resp.data} == {random_tenant.name, collaboration_tenant.name}
