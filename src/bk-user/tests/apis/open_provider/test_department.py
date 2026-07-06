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
from bkuser.apps.data_source.models import DataSourceDepartment
from bkuser.apps.tenant.models import TenantDepartment
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestDepartmentBatchCreate:
    def test_standard(self, api_client, full_local_data_source):
        resp = api_client.post(
            reverse("open_provider.department.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={
                "departments": [
                    {"id": "new_dept_1", "name": "新部门1"},
                    {"id": "new_dept_2", "name": "新部门2"},
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert DataSourceDepartment.objects.filter(data_source=full_local_data_source, code="new_dept_1").exists()
        assert DataSourceDepartment.objects.filter(data_source=full_local_data_source, code="new_dept_2").exists()


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestDepartmentBatchUpdate:
    def test_standard(self, api_client, full_local_data_source):
        ds_dept = DataSourceDepartment.objects.filter(data_source=full_local_data_source).first()

        resp = api_client.put(
            reverse("open_provider.department.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={
                "departments": [
                    {"id": ds_dept.code, "name": "更新部门名"},
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        ds_dept.refresh_from_db()
        assert ds_dept.name == "更新部门名"


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestDepartmentBatchDelete:
    def test_delete_leaf_department(self, api_client, full_local_data_source, random_tenant):
        resp = api_client.post(
            reverse("open_provider.department.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={
                "departments": [
                    {"id": "to_delete_dept", "name": "待删除部门"},
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED

        resp = api_client.delete(
            reverse("open_provider.department.batch", kwargs={"data_source_id": full_local_data_source.id}),
            data={"ids": ["to_delete_dept"]},
            format="json",
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not DataSourceDepartment.objects.filter(
            data_source=full_local_data_source, code="to_delete_dept"
        ).exists()
        assert not TenantDepartment.objects.filter(data_source_department__code="to_delete_dept").exists()
