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
from bkuser.apps.tenant.models import TenantDepartment
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantDepartmentRetrieveApi:
    def test_with_no_ancestors(self, api_client):
        company = TenantDepartment.objects.get(data_source_department__code="company")
        resp = api_client.get(
            reverse("open_v3.tenant_department.retrieve", kwargs={"id": company.id}), data={"with_ancestors": True}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == company.id
        assert resp.data["name"] == "公司"
        assert resp.data["ancestors"] == []

    def test_with_not_ancestors(self, api_client):
        center_aa = TenantDepartment.objects.get(data_source_department__code="center_aa")
        resp = api_client.get(reverse("open_v3.tenant_department.retrieve", kwargs={"id": center_aa.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == center_aa.id
        assert resp.data["name"] == "中心AA"
        assert "ancestors" not in resp.data

    def test_with_ancestors(self, api_client):
        company = TenantDepartment.objects.get(data_source_department__code="company")
        dept_a = TenantDepartment.objects.get(data_source_department__code="dept_a")
        center_aa = TenantDepartment.objects.get(data_source_department__code="center_aa")
        resp = api_client.get(
            reverse("open_v3.tenant_department.retrieve", kwargs={"id": center_aa.id}), data={"with_ancestors": True}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == center_aa.id
        assert resp.data["name"] == "中心AA"
        assert resp.data["ancestors"] == [{"id": company.id, "name": "公司"}, {"id": dept_a.id, "name": "部门A"}]

    def test_with_not_found(self, api_client):
        resp = api_client.get(reverse("open_v3.tenant_department.retrieve", kwargs={"id": 9999}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND
