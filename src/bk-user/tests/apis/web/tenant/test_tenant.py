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
from bkuser.apps.tenant.constants import TenantStatus
from bkuser.apps.tenant.models import Tenant
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestTenantCreateApi:
    def test_create(self, api_client, default_tenant):
        tenant_id = "random-tenant-2887"
        resp = api_client.post(
            reverse("tenant.list_create"),
            data={
                "id": tenant_id,
                "name": tenant_id,
                "managers": [
                    {
                        "username": "admin",
                        "full_name": "admin",
                        "email": "admin@{}.com".format(tenant_id),
                        "phone": "12345678901",
                    }
                ],
                "feature_flags": {"user_number_visible": False},
                "password_initial_config": {
                    "force_change_at_first_login": True,
                    "cannot_use_previous_password": True,
                    "reserved_previous_password_count": 5,
                    "generate_method": "random",
                    "notification": {
                        "enabled_methods": ["email"],
                        "templates": [
                            {
                                "method": "email",
                                "scene": "user_initialize",
                                "title": "初始化密码",
                                "sender": "admin",
                                "content": "您的初始密码为:{{password}}",
                                "content_html": "您的初始密码为:{{password}}",
                            }
                        ],
                    },
                },
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["id"] == tenant_id


class TestTenantListApi:
    def test_list(self, api_client, default_tenant, random_tenant):
        resp = api_client.get(reverse("tenant.list_create"))
        assert len(resp.data) >= 2  # noqa: PLR2004


class TestTenantUpdateApi:
    def test_update(self, api_client, default_tenant):
        url = reverse("tenant.retrieve_update_destroy", kwargs={"id": default_tenant.id})
        resp = api_client.put(
            url,
            data={
                "name": "default-tenant-alias",
                "manager_ids": ["admin"],
                "feature_flags": {"user_number_visible": False},
            },
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT


class TestTenantRetrieveApi:
    def test_retrieve(self, api_client, default_tenant):
        resp = api_client.get(reverse("tenant.retrieve_update_destroy", kwargs={"id": default_tenant.id}))
        assert resp.data["id"] == default_tenant.id
        assert resp.data["name"] == default_tenant.name
        assert resp.data["logo"] == ""
        assert resp.data["feature_flags"] == {"user_number_visible": True}
        assert "admin" in [m["id"] for m in resp.data["managers"]]


class TestTenantDestroyApi:
    def test_destroy(self, api_client, random_tenant):
        random_tenant.status = TenantStatus.DISABLED
        random_tenant.save()

        resp = api_client.delete(reverse("tenant.retrieve_update_destroy", kwargs={"id": random_tenant.id}))
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        assert not Tenant.objects.filter(id=random_tenant.id).exists()

    def test_destroy_enabled_tenant(self, api_client, random_tenant):
        resp = api_client.delete(reverse("tenant.retrieve_update_destroy", kwargs={"id": random_tenant.id}))
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


class TestTenantSwitchStatusApi:
    def test_switch(self, api_client, random_tenant):
        url = reverse("tenant.switch_status", kwargs={"id": random_tenant.id})
        # 默认启用，切换后不可用
        assert api_client.patch(url).data["status"] == TenantStatus.DISABLED
        # 再次切换，变成可用
        assert api_client.patch(url).data["status"] == TenantStatus.ENABLED
