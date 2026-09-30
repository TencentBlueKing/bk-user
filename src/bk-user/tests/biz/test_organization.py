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

from typing import Any, Dict, List

import pytest
from bkuser.apps.data_source.models import DataSourceDepartment
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.biz.organization import TenantOrgPathHandler

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestQueryOrganizationPath:
    """组织路径查询测试"""

    def test_query_org_path_include_self(self):
        """测试包含自身的组织路径"""
        group_aaa = DataSourceDepartment.objects.get(code="group_aaa")
        group_aba = DataSourceDepartment.objects.get(code="group_aba")

        data_source_department_ids = [group_aaa.id, group_aba.id]

        result = TenantOrgPathHandler._query_org_path(data_source_department_ids, include_self=True)

        assert result[group_aaa.id] == "公司/部门A/中心AA/小组AAA"
        assert result[group_aba.id] == "公司/部门A/中心AB/小组ABA"

    def test_query_org_path_exclude_self(self):
        """测试不包含自身的组织路径"""
        group_aaa = DataSourceDepartment.objects.get(code="group_aaa")
        center_ab = DataSourceDepartment.objects.get(code="center_ab")

        data_source_department_ids = [group_aaa.id, center_ab.id]

        result = TenantOrgPathHandler._query_org_path(data_source_department_ids, include_self=False)

        assert result[group_aaa.id] == "公司/部门A/中心AA"
        assert result[center_ab.id] == "公司/部门A"

    def test_query_org_path_root_department(self):
        """测试根部门的组织路径"""
        company = DataSourceDepartment.objects.get(code="company")

        data_source_department_ids = [company.id]

        result = TenantOrgPathHandler._query_org_path(data_source_department_ids, include_self=True)

        assert result[company.id] == "公司"

    def test_query_org_path_with_empty_input(self):
        """测试空输入"""
        data_source_department_ids: List[int] = []
        result = TenantOrgPathHandler._query_org_path(data_source_department_ids, include_self=True)
        assert result == {}


def _tenant_user(tenant, username: str) -> TenantUser:
    return TenantUser.objects.get(tenant=tenant, data_source_user__username=username)


def _ds_dept_id(code: str) -> int:
    return DataSourceDepartment.objects.get(code=code).id


def _node(tenant, code: str, name: str) -> Dict[str, Any]:
    tenant_dept = TenantDepartment.objects.get(tenant=tenant, data_source_department__code=code)
    return {"id": tenant_dept.id, "name": name}


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestGetDeptAncestorsMap:
    """部门祖先链测试"""

    def test_empty_input(self, random_tenant):
        assert TenantOrgPathHandler.get_dept_ancestors_map(random_tenant.id, []) == {}

    def test_root_and_nested_departments(self, random_tenant):
        company, dept_a, center_aa = _ds_dept_id("company"), _ds_dept_id("dept_a"), _ds_dept_id("center_aa")

        result = TenantOrgPathHandler.get_dept_ancestors_map(random_tenant.id, [company, dept_a, center_aa])

        assert result[company] == []
        assert result[dept_a] == [_node(random_tenant, "company", "公司")]
        assert result[center_aa] == [_node(random_tenant, "company", "公司"), _node(random_tenant, "dept_a", "部门A")]

    def test_ancestor_not_in_tenant(self, random_tenant):
        """祖先在当前租户未同步时，链不断开：id 为 None，name 仍保留，路径与旧逻辑一致"""
        group_aaa = _ds_dept_id("group_aaa")
        company_node = _node(random_tenant, "company", "公司")
        center_aa_node = _node(random_tenant, "center_aa", "中心AA")
        TenantDepartment.objects.filter(tenant=random_tenant, data_source_department__code="dept_a").delete()

        result = TenantOrgPathHandler.get_dept_ancestors_map(random_tenant.id, [group_aaa])

        assert result[group_aaa] == [company_node, {"id": None, "name": "部门A"}, center_aa_node]
        assert (
            "/".join(a["name"] for a in result[group_aaa])
            == TenantOrgPathHandler.get_dept_organization_path_map([group_aaa])[group_aaa]
        )


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestGetUserOrganizationsMap:
    """用户所属组织链测试"""

    def test_empty_input(self, random_tenant):
        assert TenantOrgPathHandler.get_user_organizations_map(random_tenant.id, []) == {}

    def test_user_without_department(self, random_tenant):
        freedom = _tenant_user(random_tenant, "freedom")

        result = TenantOrgPathHandler.get_user_organizations_map(random_tenant.id, [freedom])

        assert result[freedom.id] == []

    def test_root_department_user(self, random_tenant):
        """直属根部门时，链只有根部门自身"""
        zhangsan = _tenant_user(random_tenant, "zhangsan")

        result = TenantOrgPathHandler.get_user_organizations_map(random_tenant.id, [zhangsan])

        assert result[zhangsan.id] == [[_node(random_tenant, "company", "公司")]]

    def test_nested_department_includes_ancestors(self, random_tenant):
        """小组 AAA 上的用户要带上从根到直属部门的整条链"""
        liuqi = _tenant_user(random_tenant, "liuqi")

        result = TenantOrgPathHandler.get_user_organizations_map(random_tenant.id, [liuqi])

        assert result[liuqi.id] == [
            [
                _node(random_tenant, "company", "公司"),
                _node(random_tenant, "dept_a", "部门A"),
                _node(random_tenant, "center_aa", "中心AA"),
                _node(random_tenant, "group_aaa", "小组AAA"),
            ]
        ]

    def test_multi_org_user(self, random_tenant):
        """王五同时属于部门 A 和部门 B，每个直属部门一条链，共享的「公司」不去重"""
        wangwu = _tenant_user(random_tenant, "wangwu")

        result = TenantOrgPathHandler.get_user_organizations_map(random_tenant.id, [wangwu])

        assert result[wangwu.id] == [
            [_node(random_tenant, "company", "公司"), _node(random_tenant, "dept_a", "部门A")],
            [_node(random_tenant, "company", "公司"), _node(random_tenant, "dept_b", "部门B")],
        ]

    def test_aligned_with_organization_paths(self, random_tenant):
        """每条链拼接出的路径与旧的 organization_paths 逐条一致"""
        wangwu = _tenant_user(random_tenant, "wangwu")

        chains = TenantOrgPathHandler.get_user_organizations_map(random_tenant.id, [wangwu])[wangwu.id]
        paths = TenantOrgPathHandler.get_user_organization_paths_map([wangwu.data_source_user_id])

        assert ["/".join(n["name"] for n in chain) for chain in chains] == paths[wangwu.data_source_user_id]

    def test_direct_department_not_in_tenant(self, random_tenant):
        """直属部门在当前租户未同步时，仍保留该条链，末节点 id 为 None"""
        zhangsan = _tenant_user(random_tenant, "zhangsan")
        TenantDepartment.objects.filter(tenant=random_tenant, data_source_department__code="company").delete()

        result = TenantOrgPathHandler.get_user_organizations_map(random_tenant.id, [zhangsan])

        assert result[zhangsan.id] == [[{"id": None, "name": "公司"}]]
