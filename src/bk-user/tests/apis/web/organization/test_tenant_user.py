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
import random

import pytest
from bkuser.apps.tenant.models import TenantUser
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestTenantUserWithCustomField:
    def _add_extras_for_tenant_user(self, extras, tenant_id):
        tenant_users = TenantUser.objects.filter(tenant_id=tenant_id)
        for tenant_user in tenant_users:
            data_source_user = tenant_user.data_source_user
            data_source_user.extras = extras
            data_source_user.save()

    def test_retrieve_tenant_user_with_custom_field(
        self, bk_user, custom_fields, api_client, tenant_users, default_tenant
    ):
        extras = {field.name: field.default for field in custom_fields}
        self._add_extras_for_tenant_user(extras, default_tenant.id)

        user = random.choice(list(tenant_users))
        response = api_client.get(reverse("department.users.retrieve", kwargs={"id": user.id}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["extras"] == extras

        response = api_client.get(reverse("department.users.retrieve", kwargs={"id": bk_user.username}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["extras"] == extras

    def test_list_tenant_user_with_custom_field(
        self, api_client, custom_fields, tenant_users, default_tenant, tenant_departments
    ):
        extras = {field.name: field.default for field in custom_fields}
        self._add_extras_for_tenant_user(extras, default_tenant.id)

        # 租户下展示用户
        response = api_client.get(reverse("organization.tenant.users.list", kwargs={"id": default_tenant.id}))
        assert response.status_code == status.HTTP_200_OK
        for user in response.data["results"]:
            assert user["extras"] == extras

        # 部门下用户
        tenant_department = random.choice(list(tenant_departments))
        response = api_client.get(reverse("departments.users.list", kwargs={"id": tenant_department.id}))
        assert response.status_code == status.HTTP_200_OK
        for user in response.data["results"]:
            assert user["extras"] == extras
