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

from typing import List

import pytest
from bkuser.apps.data_source.models import DataSourceDepartment
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.biz.organization import TenantOrgExclusionHandler, TenantOrgPathHandler

pytestmark = pytest.mark.django_db

# full_local_data_source fixture 初始化的全部部门 / 用户，用于断言「未被排除」的补集
_ALL_DEPT_CODES = {
    "company",
    "dept_a",
    "dept_b",
    "center_aa",
    "center_ab",
    "center_ba",
    "group_aaa",
    "group_aba",
    "group_baa",
}
_ALL_USERNAMES = {
    "zhangsan",
    "lisi",
    "wangwu",
    "zhaoliu",
    "liuqi",
    "maiba",
    "yangjiu",
    "lushi",
    "linshiyi",
    "baishier",
    "freedom",
}


def _tenant_dept(tenant, code: str) -> TenantDepartment:
    return TenantDepartment.objects.get(tenant=tenant, data_source_department__code=code)


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


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestExcludeDepartments:
    """部门查询集排除：指定部门及其全部子孙部门"""

    @staticmethod
    def _exclude(tenant, excluded_department_ids):
        queryset = TenantOrgExclusionHandler.exclude_departments(
            TenantDepartment.objects.filter(tenant=tenant), tenant.id, excluded_department_ids
        )
        return set(queryset.values_list("data_source_department__code", flat=True))

    def test_empty_input(self, random_tenant):
        assert self._exclude(random_tenant, []) == _ALL_DEPT_CODES

    def test_middle_department_excludes_descendants(self, random_tenant):
        """中层部门应连带排除自身 + 全部子孙"""
        dept_a = _tenant_dept(random_tenant, "dept_a")

        assert self._exclude(random_tenant, [dept_a.id]) == {"company", "dept_b", "center_ba", "group_baa"}

    def test_leaf_department_excludes_only_self(self, random_tenant):
        group_aaa = _tenant_dept(random_tenant, "group_aaa")

        assert self._exclude(random_tenant, [group_aaa.id]) == _ALL_DEPT_CODES - {"group_aaa"}

    def test_root_department_excludes_whole_tree(self, random_tenant):
        """根部门应排除整棵树"""
        company = _tenant_dept(random_tenant, "company")

        assert self._exclude(random_tenant, [company.id]) == set()

    def test_multi_departments_merged(self, random_tenant):
        center_aa = _tenant_dept(random_tenant, "center_aa")
        dept_b = _tenant_dept(random_tenant, "dept_b")

        assert self._exclude(random_tenant, [center_aa.id, dept_b.id]) == {
            "company",
            "dept_a",
            "center_ab",
            "group_aba",
        }

    def test_overlapped_departments(self, random_tenant):
        """父子部门同时传入时，结果与只传父部门一致"""
        dept_a = _tenant_dept(random_tenant, "dept_a")
        center_aa = _tenant_dept(random_tenant, "center_aa")

        assert self._exclude(random_tenant, [dept_a.id, center_aa.id]) == self._exclude(random_tenant, [dept_a.id])

    def test_not_exists_department(self, random_tenant):
        assert self._exclude(random_tenant, [99999999]) == _ALL_DEPT_CODES

    def test_other_tenant_department(self, random_tenant):
        """排除使用的是当前请求租户下的部门 ID，其他租户的部门 ID 不生效"""
        dept_a = _tenant_dept(random_tenant, "dept_a")

        queryset = TenantOrgExclusionHandler.exclude_departments(
            TenantDepartment.objects.filter(tenant=random_tenant), "not_exists_tenant", [dept_a.id]
        )

        assert set(queryset.values_list("data_source_department__code", flat=True)) == _ALL_DEPT_CODES


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestExcludeUsers:
    """用户查询集排除：指定用户 + 归属在被排除部门子树上的用户"""

    @staticmethod
    def _exclude(tenant, excluded_department_ids=None, excluded_user_ids=None):
        queryset = TenantOrgExclusionHandler.exclude_users(
            TenantUser.objects.filter(tenant=tenant),
            tenant.id,
            excluded_department_ids or [],
            excluded_user_ids or [],
        )
        return set(queryset.values_list("data_source_user__username", flat=True))

    def test_empty_input(self, random_tenant):
        assert self._exclude(random_tenant) == _ALL_USERNAMES

    def test_exclude_user_ids(self, random_tenant):
        lisi = TenantUser.objects.get(tenant=random_tenant, data_source_user__username="lisi")

        assert self._exclude(random_tenant, excluded_user_ids=[lisi.id]) == _ALL_USERNAMES - {"lisi"}

    def test_exclude_department_subtree(self, random_tenant):
        """挂在「部门A」子树上的用户全部排除，含多组织用户 wangwu / lushi"""
        dept_a = _tenant_dept(random_tenant, "dept_a")

        # 「部门A」子树上有 lisi、wangwu、zhaoliu、liuqi、maiba、yangjiu、lushi、linshiyi
        assert self._exclude(random_tenant, excluded_department_ids=[dept_a.id]) == {
            "zhangsan",
            "baishier",
            "freedom",
        }

    def test_exclude_root_department(self, random_tenant):
        """排除根部门时，除无部门用户外全部排除"""
        company = _tenant_dept(random_tenant, "company")

        assert self._exclude(random_tenant, excluded_department_ids=[company.id]) == {"freedom"}

    def test_no_department_user_not_affected_by_department(self, random_tenant):
        """无部门用户不受 excluded_department_ids 影响"""
        company = _tenant_dept(random_tenant, "company")

        assert "freedom" in self._exclude(random_tenant, excluded_department_ids=[company.id])

    def test_combined_exclusion(self, random_tenant):
        dept_a = _tenant_dept(random_tenant, "dept_a")
        zhangsan = TenantUser.objects.get(tenant=random_tenant, data_source_user__username="zhangsan")

        assert self._exclude(random_tenant, excluded_department_ids=[dept_a.id], excluded_user_ids=[zhangsan.id]) == {
            "baishier",
            "freedom",
        }
