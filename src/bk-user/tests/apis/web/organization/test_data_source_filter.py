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
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceUser,
)
from bkuser.apps.tenant.constants import TenantUserStatus
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.plugins.local.models import LocalDataSourcePluginConfig
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def _create_local_data_source(tenant_id, plugin, plugin_cfg, name) -> DataSource:
    return DataSource.objects.create(
        owner_tenant_id=tenant_id,
        name=name,
        type=DataSourceTypeEnum.REAL,
        plugin=plugin,
        plugin_config=LocalDataSourcePluginConfig(**plugin_cfg),
    )


def _create_root_tenant_department(data_source, tenant, code, name) -> TenantDepartment:
    ds_dept = DataSourceDepartment.objects.create(data_source=data_source, code=code, name=name)
    DataSourceDepartmentRelation.objects.create(department=ds_dept, parent=None, data_source=data_source)
    return TenantDepartment.objects.create(tenant=tenant, data_source=data_source, data_source_department=ds_dept)


def _create_tenant_user(data_source, tenant, code, username, uid) -> TenantUser:
    ds_user = DataSourceUser.objects.create(
        data_source=data_source,
        code=code,
        username=username,
        full_name=username,
        email=f"{username}@example.com",
        phone="13500000000",
    )
    return TenantUser.objects.create(id=uid, tenant=tenant, data_source=data_source, data_source_user=ds_user)


class TestTenantDepartmentListDataSourceFilter:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_list_root_depts_isolated_by_path(
        self, api_client, random_tenant, full_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        ds_a = full_local_data_source
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        _create_root_tenant_department(ds_b, random_tenant, "root_b", "总部B")

        resp = api_client.get(
            reverse("organization.tenant_department.list_create", kwargs={"data_source_id": ds_a.id}),
            data={"parent_department_id": 0},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert {d["data_source_id"] for d in resp.data} == {ds_a.id}
        assert {d["name"] for d in resp.data} == {"公司"}

        resp = api_client.get(
            reverse("organization.tenant_department.list_create", kwargs={"data_source_id": ds_b.id}),
            data={"parent_department_id": 0},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert {d["data_source_id"] for d in resp.data} == {ds_b.id}
        assert {d["name"] for d in resp.data} == {"总部B"}

    def test_child_filter_rejects_cross_source_parent(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        root_a = _create_root_tenant_department(bare_local_data_source, random_tenant, "root_a", "总部A")

        resp = api_client.get(
            reverse("organization.tenant_department.list_create", kwargs={"data_source_id": ds_b.id}),
            data={"parent_department_id": root_a.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data == []

    def test_rejects_unknown_data_source_id(self, api_client, random_tenant):
        resp = api_client.get(
            reverse("organization.tenant_department.list_create", kwargs={"data_source_id": 0}),
            data={"parent_department_id": 0},
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST


class TestTenantUserListDataSourceFilter:
    def test_filter_users_by_data_source(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        ds_a = bare_local_data_source
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        _create_tenant_user(ds_a, random_tenant, "ua", "user_a", "uid_user_a")
        _create_tenant_user(ds_b, random_tenant, "ub", "user_b", "uid_user_b")

        resp = api_client.get(
            reverse("organization.tenant_user.list_create", kwargs={"data_source_id": ds_a.id}),
            data={"recursive": True, "department_id": 0},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert {u["data_source_id"] for u in resp.data["results"]} == {ds_a.id}
        assert {u["username"] for u in resp.data["results"]} == {"user_a"}

        resp = api_client.get(
            reverse("organization.tenant_user.list_create", kwargs={"data_source_id": ds_b.id}),
            data={"recursive": True, "department_id": 0},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert {u["data_source_id"] for u in resp.data["results"]} == {ds_b.id}
        assert {u["username"] for u in resp.data["results"]} == {"user_b"}

        # 租户维列表覆盖该租户下全部实名源用户
        resp = api_client.get(reverse("organization.tenant_user.list", kwargs={"tenant_id": random_tenant.id}))
        assert resp.status_code == status.HTTP_200_OK
        assert {u["data_source_id"] for u in resp.data["results"]} == {ds_a.id, ds_b.id}

    def test_rejects_unknown_data_source_id(self, api_client, random_tenant):
        resp = api_client.get(
            reverse("organization.tenant_user.list_create", kwargs={"data_source_id": 0}),
            data={"recursive": True, "department_id": 0},
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST


class TestTenantUserBatchDataSourceIsolation:
    def test_status_update_allows_users_from_multiple_data_sources(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        ds_a = bare_local_data_source
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        user_a = _create_tenant_user(ds_a, random_tenant, "batch_a", "batch_a", "uid_batch_a")
        user_b = _create_tenant_user(ds_b, random_tenant, "batch_b", "batch_b", "uid_batch_b")

        resp = api_client.put(
            reverse("organization.tenant_user.status.batch_update"),
            data={
                "user_ids": [user_a.id, user_b.id],
                "status": TenantUserStatus.DISABLED,
            },
        )

        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert TenantUser.objects.get(id=user_a.id).status == TenantUserStatus.DISABLED
        assert TenantUser.objects.get(id=user_b.id).status == TenantUserStatus.DISABLED

    def test_custom_field_update_rejects_users_from_another_data_source(
        self,
        api_client,
        random_tenant,
        bare_local_data_source,
        local_ds_plugin,
        local_ds_plugin_cfg,
        random_tenant_custom_fields,
    ):
        ds_a = bare_local_data_source
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        user_a = _create_tenant_user(ds_a, random_tenant, "cf_a", "cf_a", "uid_cf_a")
        user_b = _create_tenant_user(ds_b, random_tenant, "cf_b", "cf_b", "uid_cf_b")
        age_field = random_tenant_custom_fields[0]

        resp = api_client.put(
            reverse("organization.tenant_user.custom_field.batch_update", kwargs={"data_source_id": ds_a.id}),
            data={
                "user_ids": [user_a.id, user_b.id],
                "field_name": age_field.name,
                "value": {age_field.name: 18},
            },
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST


class TestTenantDepartmentSearchDataSourceFilter:
    def test_search_returns_data_source_id(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        ds_a = bare_local_data_source
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        _create_root_tenant_department(ds_a, random_tenant, "rd_a", "研发中心")
        _create_root_tenant_department(ds_b, random_tenant, "rd_b", "研发中心")

        resp = api_client.get(reverse("organization.tenant_department.search"), data={"keyword": "研发"})
        assert resp.status_code == status.HTTP_200_OK
        assert all("data_source_id" in d for d in resp.data)
        assert {d["data_source_id"] for d in resp.data} == {ds_a.id, ds_b.id}


class TestTenantUserSearchDataSourceFilter:
    def test_search_returns_data_source_id(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        ds_a = bare_local_data_source
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        _create_tenant_user(ds_a, random_tenant, "sa", "searchuser_a", "uid_search_a")
        _create_tenant_user(ds_b, random_tenant, "sb", "searchuser_b", "uid_search_b")

        resp = api_client.get(reverse("organization.tenant_user.search"), data={"keyword": "searchuser"})
        assert resp.status_code == status.HTTP_200_OK
        assert all("data_source_id" in u for u in resp.data)
        assert {u["data_source_id"] for u in resp.data} == {ds_a.id, ds_b.id}


class TestTenantDepartmentCreateDataSourceBinding:
    def test_create_root_binds_data_source(self, api_client, random_tenant, bare_local_data_source):
        resp = api_client.post(
            reverse(
                "organization.tenant_department.list_create",
                kwargs={"data_source_id": bare_local_data_source.id},
            ),
            data={"parent_department_id": 0, "name": "研发中心"},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        dept = TenantDepartment.objects.get(id=resp.data["id"])
        assert dept.data_source_id == bare_local_data_source.id

    def test_create_child_binds_parent_source(self, api_client, random_tenant, bare_local_data_source):
        root = _create_root_tenant_department(bare_local_data_source, random_tenant, "root_a", "总部A")
        resp = api_client.post(
            reverse(
                "organization.tenant_department.list_create",
                kwargs={"data_source_id": bare_local_data_source.id},
            ),
            data={"parent_department_id": root.id, "name": "后端组"},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        dept = TenantDepartment.objects.get(id=resp.data["id"])
        assert dept.data_source_id == bare_local_data_source.id

    def test_create_child_cross_source_rejected(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        root_a = _create_root_tenant_department(bare_local_data_source, random_tenant, "root_a", "总部A")
        resp = api_client.post(
            reverse("organization.tenant_department.list_create", kwargs={"data_source_id": ds_b.id}),
            data={"parent_department_id": root_a.id, "name": "子部门"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "父部门不属于当前的数据源" in resp.data["message"]

    def test_create_on_external_source_rejected(self, api_client, random_tenant, bare_general_data_source):
        resp = api_client.post(
            reverse(
                "organization.tenant_department.list_create",
                kwargs={"data_source_id": bare_general_data_source.id},
            ),
            data={"parent_department_id": 0, "name": "研发"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "指定的本地实名数据源不存在" in resp.data["message"]


class TestOptionalListDataSourceIsolation:
    """候选上级 / 候选部门按路径中的 data_source_id 隔离"""

    def test_optional_leaders_isolated_by_data_source(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        ds_a = bare_local_data_source
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        _create_tenant_user(ds_a, random_tenant, "ola", "opt_leader_a", "uid_opt_leader_a")
        _create_tenant_user(ds_b, random_tenant, "olb", "opt_leader_b", "uid_opt_leader_b")

        resp = api_client.get(
            reverse("organization.optional_leader.list", kwargs={"data_source_id": ds_a.id}),
            data={"keyword": "opt_leader"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert {u["username"] for u in resp.data} == {"opt_leader_a"}

        resp = api_client.get(
            reverse("organization.optional_leader.list", kwargs={"data_source_id": ds_b.id}),
            data={"keyword": "opt_leader"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert {u["username"] for u in resp.data} == {"opt_leader_b"}

    def test_optional_leaders_reject_external_data_source(self, api_client, random_tenant, bare_general_data_source):
        resp = api_client.get(
            reverse("organization.optional_leader.list", kwargs={"data_source_id": bare_general_data_source.id}),
            data={"keyword": "x"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_optional_departments_isolated_by_data_source(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        ds_a = bare_local_data_source
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        _create_root_tenant_department(ds_a, random_tenant, "opt_rd_a", "可选部门A")
        _create_root_tenant_department(ds_b, random_tenant, "opt_rd_b", "可选部门B")

        resp = api_client.get(
            reverse("organization.optional_department.list", kwargs={"data_source_id": ds_a.id}),
            data={"keyword": "可选部门"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert {d["name"] for d in resp.data} == {"可选部门A"}

        resp = api_client.get(
            reverse("organization.optional_department.list", kwargs={"data_source_id": ds_b.id}),
            data={"keyword": "可选部门"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert {d["name"] for d in resp.data} == {"可选部门B"}

    def test_optional_departments_reject_external_data_source(
        self, api_client, random_tenant, bare_general_data_source
    ):
        resp = api_client.get(
            reverse("organization.optional_department.list", kwargs={"data_source_id": bare_general_data_source.id}),
            data={"keyword": "x"},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
