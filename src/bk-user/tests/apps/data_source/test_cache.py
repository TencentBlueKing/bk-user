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
from bkuser.apps.data_source.cache import DepartmentAncestorCache
from bkuser.apps.data_source.models import DataSourceDepartment

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestDepartmentAncestorCache:
    """部门祖先缓存测试"""

    def test_batch_get_with_empty_input(self):
        """测试空输入场景"""
        cache = DepartmentAncestorCache()
        result = cache.batch_get([])
        assert result == {}

    def test_batch_get_root_department(self):
        """测试获取根部门的祖先"""
        cache = DepartmentAncestorCache()
        company_dept = DataSourceDepartment.objects.get(code="company")
        result = cache.batch_get([company_dept.id])

        assert company_dept.id in result
        assert result[company_dept.id] == []

    def test_batch_get_with_multi_level_department(self):
        """测试获取多层级部门的祖先"""
        cache = DepartmentAncestorCache()
        company = DataSourceDepartment.objects.get(code="company")
        dept_a = DataSourceDepartment.objects.get(code="dept_a")
        center_aa = DataSourceDepartment.objects.get(code="center_aa")
        group_aaa = DataSourceDepartment.objects.get(code="group_aaa")

        result = cache.batch_get([group_aaa.id])
        assert group_aaa.id in result

        ancestors = result[group_aaa.id]
        assert len(ancestors) == 3
        assert company.id in ancestors
        assert dept_a.id in ancestors
        assert center_aa.id in ancestors

    def test_batch_get_multiple_departments(self):
        """测试批量获取多个部门的祖先"""
        cache = DepartmentAncestorCache()
        company_dept = DataSourceDepartment.objects.get(code="company")
        dept_a = DataSourceDepartment.objects.get(code="dept_a")
        center_aa = DataSourceDepartment.objects.get(code="center_aa")
        group_aaa = DataSourceDepartment.objects.get(code="group_aaa")
        dept_ids = [company_dept.id, dept_a.id, center_aa.id, group_aaa.id]

        result = cache.batch_get(dept_ids)

        assert len(result) == 4
        assert company_dept.id in result
        assert dept_a.id in result
        assert center_aa.id in result
        assert group_aaa.id in result

        assert result[company_dept.id] == []
        assert len(result[dept_a.id]) == 1
        assert len(result[center_aa.id]) == 2
        assert len(result[group_aaa.id]) == 3

    def test_batch_get_with_cache_hit(self):
        """测试缓存命中场景"""
        cache = DepartmentAncestorCache()
        dept_a = DataSourceDepartment.objects.get(code="dept_a")

        # 第一次调用，从数据库查询并缓存
        result1 = cache.batch_get([dept_a.id])

        # 第二次调用，应该从缓存获取
        result2 = cache.batch_get([dept_a.id])

        # 两次结果应该一致
        assert result1 == result2

    def test_batch_delete(self):
        """测试批量删除缓存"""
        cache = DepartmentAncestorCache()
        dept_a = DataSourceDepartment.objects.get(code="dept_a")
        center_aa = DataSourceDepartment.objects.get(code="center_aa")

        # 先缓存数据
        cache.batch_get([dept_a.id, center_aa.id])

        # 删除缓存
        cache.batch_delete([dept_a.id, center_aa.id])

        # 再次查询应该从数据库获取
        result = cache.batch_get([dept_a.id, center_aa.id])
        assert len(result) == 2
