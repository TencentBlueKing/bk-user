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


class TestTenantRetrieveApi:
    def test_with_current_tenant(self, api_client, random_tenant):
        resp = api_client.get(reverse("open_web.tenant.retrieve"))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == random_tenant.id
        assert resp.data["name"] == random_tenant.name
        assert resp.data["collab_tenants"] == []

    @pytest.mark.usefixtures("_init_collaboration_users_depts")
    def test_with_all_data(self, api_client, random_tenant, collaboration_tenant):
        resp = api_client.get(reverse("open_web.tenant.retrieve"))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == random_tenant.id
        assert resp.data["name"] == random_tenant.name
        assert resp.data["collab_tenants"] == [{"id": collaboration_tenant.id, "name": collaboration_tenant.name}]
