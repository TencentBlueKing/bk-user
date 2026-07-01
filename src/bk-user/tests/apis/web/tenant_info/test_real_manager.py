# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
from bkuser.apps.tenant.models import TenantManager, TenantUser
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestTenantRealManagerDestroy:
    """测试批量移除租户实名管理员"""

    def test_delete_other_manager(self, api_client, random_tenant, real_manager, another_real_manager):
        """正常移除其他管理员"""
        resp = api_client.delete(
            reverse("tenant_info.list_create_destroy_real_manager"),
            QUERY_STRING=f"ids={another_real_manager.tenant_user_id}",
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not TenantManager.objects.filter(
            tenant=random_tenant, tenant_user=another_real_manager.tenant_user
        ).exists()

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_cannot_delete_self(self, bk_user, api_client, random_tenant, real_manager):
        """管理员不能移除自己"""
        current_user_id = bk_user.username

        # 确保当前用户也是实名管理员
        tenant_user = TenantUser.objects.get(id=current_user_id, tenant=random_tenant)
        TenantManager.objects.get_or_create(tenant=random_tenant, tenant_user=tenant_user)

        resp = api_client.delete(
            reverse("tenant_info.list_create_destroy_real_manager"),
            QUERY_STRING=f"ids={current_user_id}",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_cannot_delete_self_in_batch(self, bk_user, api_client, random_tenant, another_real_manager):
        """批量移除时包含自己也应被拒绝"""
        current_user_id = bk_user.username

        tenant_user = TenantUser.objects.get(id=current_user_id, tenant=random_tenant)
        TenantManager.objects.get_or_create(tenant=random_tenant, tenant_user=tenant_user)

        ids = f"{current_user_id},{another_real_manager.tenant_user_id}"
        resp = api_client.delete(
            reverse("tenant_info.list_create_destroy_real_manager"),
            QUERY_STRING=f"ids={ids}",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
