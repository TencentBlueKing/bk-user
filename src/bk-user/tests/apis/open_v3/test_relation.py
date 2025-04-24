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
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantDepartmentUserRelationListApi:
    def test_list(self, api_client):
        zhangsan = TenantUser.objects.get(data_source_user__username="zhangsan")
        lisi = TenantUser.objects.get(data_source_user__username="lisi")
        wangwu = TenantUser.objects.get(data_source_user__username="wangwu")
        zhaoliu = TenantUser.objects.get(data_source_user__username="zhaoliu")
        company = TenantDepartment.objects.get(data_source_department__code="company")
        dept_a = TenantDepartment.objects.get(data_source_department__code="dept_a")
        center_aa = TenantDepartment.objects.get(data_source_department__code="center_aa")

        resp = api_client.get(
            reverse("open_v3.tenant_department_user_relation.list"), data={"page": 1, "page_size": 5}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 13
        assert {t["bk_username"] for t in resp.data["results"]} == {zhangsan.id, lisi.id, wangwu.id, zhaoliu.id}
        assert {t["department_id"] for t in resp.data["results"]} == {company.id, dept_a.id, center_aa.id}
