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
    def test_filter_root_depts_by_data_source(
        self, api_client, random_tenant, full_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        # 源 A：full_local_data_source，根部门「公司」已同步
        ds_a = full_local_data_source
        # 源 B：再建一个本地实名源 + 一个根部门
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        _create_root_tenant_department(ds_b, random_tenant, "root_b", "总部B")

        url = reverse("organization.tenant_department.list_create", kwargs={"id": random_tenant.id})

        # 不传 data_source_id -> 两源根部门都返回
        resp = api_client.get(url, data={"parent_department_id": 0})
        assert resp.status_code == status.HTTP_200_OK
        assert {d["data_source_id"] for d in resp.data} == {ds_a.id, ds_b.id}

        # 传 data_source_id=B -> 仅 B 的根部门
        resp = api_client.get(url, data={"parent_department_id": 0, "data_source_id": ds_b.id})
        assert resp.status_code == status.HTTP_200_OK
        assert {d["data_source_id"] for d in resp.data} == {ds_b.id}
        assert {d["name"] for d in resp.data} == {"总部B"}


class TestTenantUserListDataSourceFilter:
    def test_filter_users_by_data_source(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        # 源 A / 源 B 各挂一个游离用户（用户名各不相同）
        ds_a = bare_local_data_source
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        _create_tenant_user(ds_a, random_tenant, "ua", "user_a", "uid_user_a")
        _create_tenant_user(ds_b, random_tenant, "ub", "user_b", "uid_user_b")

        url = reverse("organization.tenant_user.list_create", kwargs={"id": random_tenant.id})

        # 不传 data_source_id -> 两源用户都返回
        resp = api_client.get(url, data={"recursive": True, "department_id": 0})
        assert resp.status_code == status.HTTP_200_OK
        assert {u["data_source_id"] for u in resp.data["results"]} == {ds_a.id, ds_b.id}

        # 传 data_source_id=A -> 仅 A 的用户
        resp = api_client.get(url, data={"recursive": True, "department_id": 0, "data_source_id": ds_a.id})
        assert resp.status_code == status.HTTP_200_OK
        assert {u["data_source_id"] for u in resp.data["results"]} == {ds_a.id}
        assert {u["username"] for u in resp.data["results"]} == {"user_a"}


class TestTenantDepartmentSearchDataSourceFilter:
    def test_search_filter_by_data_source(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        # 两个源各有一个同名根部门「研发中心」（跨源同名允许）
        ds_a = bare_local_data_source
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        _create_root_tenant_department(ds_a, random_tenant, "rd_a", "研发中心")
        _create_root_tenant_department(ds_b, random_tenant, "rd_b", "研发中心")

        url = reverse("organization.tenant_department.search")

        # 不传 data_source_id -> 两源都命中
        resp = api_client.get(url, data={"keyword": "研发"})
        assert resp.status_code == status.HTTP_200_OK
        assert {d["data_source_id"] for d in resp.data} == {ds_a.id, ds_b.id}

        # 传 data_source_id=A -> 仅 A
        resp = api_client.get(url, data={"keyword": "研发", "data_source_id": ds_a.id})
        assert resp.status_code == status.HTTP_200_OK
        assert {d["data_source_id"] for d in resp.data} == {ds_a.id}


class TestTenantUserSearchDataSourceFilter:
    def test_search_returns_data_source_id_and_filters(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        ds_a = bare_local_data_source
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        _create_tenant_user(ds_a, random_tenant, "sa", "searchuser_a", "uid_search_a")
        _create_tenant_user(ds_b, random_tenant, "sb", "searchuser_b", "uid_search_b")

        url = reverse("organization.tenant_user.search")

        # 结果均返回 data_source_id，且不传过滤 -> 两源都命中
        resp = api_client.get(url, data={"keyword": "searchuser"})
        assert resp.status_code == status.HTTP_200_OK
        assert all("data_source_id" in u for u in resp.data)
        assert {u["data_source_id"] for u in resp.data} == {ds_a.id, ds_b.id}

        # 传 data_source_id=A -> 仅 A
        resp = api_client.get(url, data={"keyword": "searchuser", "data_source_id": ds_a.id})
        assert resp.status_code == status.HTTP_200_OK
        assert {u["data_source_id"] for u in resp.data} == {ds_a.id}


class TestTenantDepartmentCreateDataSourceBinding:
    def test_create_root_requires_data_source_id(self, api_client, random_tenant, bare_local_data_source):
        url = reverse("organization.tenant_department.list_create", kwargs={"id": random_tenant.id})
        # 建根部门不传 data_source_id -> 400
        resp = api_client.post(url, data={"parent_department_id": 0, "name": "研发中心"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_root_binds_data_source(self, api_client, random_tenant, bare_local_data_source):
        url = reverse("organization.tenant_department.list_create", kwargs={"id": random_tenant.id})
        resp = api_client.post(
            url, data={"parent_department_id": 0, "name": "研发中心", "data_source_id": bare_local_data_source.id}
        )
        assert resp.status_code == status.HTTP_201_CREATED
        dept = TenantDepartment.objects.get(id=resp.data["id"])
        assert dept.data_source_id == bare_local_data_source.id

    def test_create_child_binds_parent_source(self, api_client, random_tenant, bare_local_data_source):
        root = _create_root_tenant_department(bare_local_data_source, random_tenant, "root_a", "总部A")
        url = reverse("organization.tenant_department.list_create", kwargs={"id": random_tenant.id})
        resp = api_client.post(
            url,
            data={"parent_department_id": root.id, "name": "后端组", "data_source_id": bare_local_data_source.id},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        dept = TenantDepartment.objects.get(id=resp.data["id"])
        assert dept.data_source_id == bare_local_data_source.id

    def test_create_child_cross_source_rejected(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        root_a = _create_root_tenant_department(bare_local_data_source, random_tenant, "root_a", "总部A")
        url = reverse("organization.tenant_department.list_create", kwargs={"id": random_tenant.id})
        # 父部门在 A，却传 data_source_id=B -> 跨源拒绝
        resp = api_client.post(
            url, data={"parent_department_id": root_a.id, "name": "子部门", "data_source_id": ds_b.id}
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_on_external_source_rejected(self, api_client, random_tenant, bare_general_data_source):
        url = reverse("organization.tenant_department.list_create", kwargs={"id": random_tenant.id})
        # 外部（通用 HTTP）源不允许创建部门
        resp = api_client.post(
            url, data={"parent_department_id": 0, "name": "研发", "data_source_id": bare_general_data_source.id}
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


class TestOptionalListDataSourceIsolation:
    """候选上级 / 候选部门按 data_source_id 隔离（Task 7）"""

    def test_optional_leaders_isolated_by_data_source(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        ds_a = bare_local_data_source
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        _create_tenant_user(ds_a, random_tenant, "ola", "opt_leader_a", "uid_opt_leader_a")
        _create_tenant_user(ds_b, random_tenant, "olb", "opt_leader_b", "uid_opt_leader_b")

        url = reverse("organization.optional_leader.list")
        resp = api_client.get(url, data={"keyword": "opt_leader", "data_source_id": ds_a.id})
        assert resp.status_code == status.HTTP_200_OK
        assert {u["username"] for u in resp.data} == {"opt_leader_a"}

        resp = api_client.get(url, data={"keyword": "opt_leader", "data_source_id": ds_b.id})
        assert resp.status_code == status.HTTP_200_OK
        assert {u["username"] for u in resp.data} == {"opt_leader_b"}

    def test_optional_leaders_reject_external_data_source(self, api_client, random_tenant, bare_general_data_source):
        resp = api_client.get(
            reverse("organization.optional_leader.list"),
            data={"keyword": "x", "data_source_id": bare_general_data_source.id},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_optional_departments_isolated_by_data_source(
        self, api_client, random_tenant, bare_local_data_source, local_ds_plugin, local_ds_plugin_cfg
    ):
        ds_a = bare_local_data_source
        ds_b = _create_local_data_source(random_tenant.id, local_ds_plugin, local_ds_plugin_cfg, "本地数据源B")
        _create_root_tenant_department(ds_a, random_tenant, "opt_rd_a", "可选部门A")
        _create_root_tenant_department(ds_b, random_tenant, "opt_rd_b", "可选部门B")

        url = reverse("organization.optional_department.list")
        resp = api_client.get(url, data={"keyword": "可选部门", "data_source_id": ds_a.id})
        assert resp.status_code == status.HTTP_200_OK
        assert {d["name"] for d in resp.data} == {"可选部门A"}

        resp = api_client.get(url, data={"keyword": "可选部门", "data_source_id": ds_b.id})
        assert resp.status_code == status.HTTP_200_OK
        assert {d["name"] for d in resp.data} == {"可选部门B"}

    def test_optional_departments_reject_external_data_source(
        self, api_client, random_tenant, bare_general_data_source
    ):
        resp = api_client.get(
            reverse("organization.optional_department.list"),
            data={"keyword": "x", "data_source_id": bare_general_data_source.id},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
