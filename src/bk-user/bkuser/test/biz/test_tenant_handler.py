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
from bkuser.apps.tenant.models import Tenant, TenantDataSourceRelationShip, TenantManager, TenantUser
from bkuser.biz.tenant_handler import tenant_handler

pytestmark = pytest.mark.django_db


class TestTenantHandler:
    def test_create_tenant(self):
        test_create_tenant_data = {
            "id": "test-fake",
            "name": "test-fake",
            "enabled_user_count_display": False,
            "logo": "",
        }
        instance = tenant_handler.create_tenant(test_create_tenant_data)
        return instance

    def test_update_tenant(self, default_tenant):
        test_update_tenant_data = {
            "id": "test-fake-2",
            "name": "test-fake-2",
            "enabled_user_count_display": True,
            "logo": "",
        }
        instance = tenant_handler.update_tenant(default_tenant, test_update_tenant_data)
        assert instance.id != test_update_tenant_data["id"]
        assert instance.name == test_update_tenant_data["name"]
        assert instance.logo == test_update_tenant_data["logo"]
        assert instance.enabled_user_count_display == test_update_tenant_data["enabled_user_count_display"]

    def test_data_source_bind_tenant(self, default_tenant, default_local_data_source):
        tenant_handler.data_source_bind_tenant(default_tenant.id, default_local_data_source.id)

        assert TenantDataSourceRelationShip.objects.filter(
            tenant_id=default_tenant.id, data_source_id=default_local_data_source.id
        ).exists()

    @pytest.fixture(name="tenant_users")
    def test_data_source_users_bind_tenant(self, default_tenant, default_local_data_source_users):
        tenant_handler.data_source_users_bind_tenant(default_tenant.id, default_local_data_source_users)

        tenant_users = TenantUser.objects.filter(tenant_id=default_tenant.id)
        assert tenant_users.exists()
        assert TenantUser.objects.filter(tenant_id=default_tenant.id).count() == len(default_local_data_source_users)
        return tenant_users

    def test_update_tenant_managers(self, default_tenant, tenant_users):
        assert tenant_users.exists()
        tenant_user_ids = [str(item) for item in tenant_users.values_list("id", flat=True)]
        tenant_handler.update_tenant_managers(default_tenant.id, tenant_user_ids)

        assert TenantManager.objects.filter(tenant_id=default_tenant.id, tenant_user_id__in=tenant_users).exists()
        assert TenantManager.objects.filter(
            tenant_id=default_tenant.id, tenant_user_id__in=tenant_users
        ).count() == len(tenant_users)

    @pytest.mark.parametrize(
        "tenant_data",
        [
            {
                "id": "test_id",
                "name": "test_name",
                "enabled_user_count_display": 0,
                "password_settings": {"init_password": "1234", "init_password_method": "fixed_preset"},
                "managers": [
                    {
                        "username": "fake_admin",
                        "telephone": "12345678901",
                        "email": "test@qq.com",
                        "display_name": "fake_admin",
                    }
                ],
            }
        ],
    )
    def test_init_tenant_with_mangers(self, tenant_data):
        tenant_handler.init_tenant_with_managers(tenant_data)
        assert Tenant.objects.filter(id=tenant_data["id"]).exists()
