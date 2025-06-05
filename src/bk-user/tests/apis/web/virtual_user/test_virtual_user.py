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
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.models import TenantUser
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestVirtualUserCreateApi:
    def test_create_virtual_user_success(self, api_client, valid_data, create_real_owner, random_tenant):
        create_real_owner(random_tenant)
        url = reverse("virtual_user.list_create")
        data = valid_data
        resp = api_client.post(
            url,
            data=data,
        )
        assert resp.status_code == status.HTTP_201_CREATED
        data_source_user = DataSourceUser.objects.get(username=data["username"])
        tenant_user = TenantUser.objects.get(data_source_user=data_source_user)
        assert resp.data["id"] == tenant_user.id
        assert DataSourceUser.objects.filter(username=data["username"]).exists()

    def test_create_virtual_user_duplicate_username(self, api_client, valid_data, create_real_owner, random_tenant):
        create_real_owner(random_tenant)
        url = reverse("virtual_user.list_create")
        data = valid_data
        resp = api_client.post(url, data=data)
        assert resp.status_code == status.HTTP_201_CREATED

        # 第二次创建应失败
        resp = api_client.post(url, data=data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert f"用户名 {valid_data['username']} 已存在" in resp.data["message"]

    def test_create_virtual_user_invalid_owner(self, api_client, valid_data, create_real_owner, random_tenant):
        create_real_owner(random_tenant)
        data = valid_data.copy()
        data["owners"] = ["invalid_owner"]
        resp = api_client.post(reverse("virtual_user.list_create"), data=data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "用户 invalid_owner 不存在" in resp.data["message"]

    def test_create_virtual_user_duplicate_app_codes(self, api_client, valid_data, create_real_owner, random_tenant):
        create_real_owner(random_tenant)
        data = valid_data.copy()
        data["app_codes"] = ["app_code_1", "app_code_1", "app_code_2"]
        resp = api_client.post(reverse("virtual_user.list_create"), data=data)
        assert resp.status_code == status.HTTP_201_CREATED

        # 获取创建的租户用户
        tenant_user = TenantUser.objects.get(id=resp.data["id"])
        # 验证实际存储的 app_code 已去重
        assert list(tenant_user.virtualuserapprelation_set.all().values_list("app_code", flat=True)) == [
            "app_code_1",
            "app_code_2",
        ]

    def test_create_virtual_user_relations(self, api_client, valid_data, create_real_owner, random_tenant):
        create_real_owner(random_tenant)
        resp = api_client.post(reverse("virtual_user.list_create"), data=valid_data)
        assert resp.status_code == status.HTTP_201_CREATED

        tenant_user = TenantUser.objects.get(id=resp.data["id"])
        # 验证应用关联
        assert set(tenant_user.virtualuserapprelation_set.values_list("app_code", flat=True)) == set(
            valid_data["app_codes"]
        )
        # 验证责任人关联
        assert {rel.owner.data_source_user.username for rel in tenant_user.virtualuserownerrelation_set.all()} == set(
            valid_data["owners"]
        )
