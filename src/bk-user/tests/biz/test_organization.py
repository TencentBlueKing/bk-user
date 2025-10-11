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

from typing import List

import pytest
from bkuser.apps.data_source.models import DataSourceDepartment
from bkuser.biz.organization import TenantOrgPathHandler

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestTenantOrgPathHandler:
    """组织路径处理器测试"""

    def test_query_org_path_include_self(self, full_local_data_source):
        """测试包含自身的组织路径"""
        group_aaa = DataSourceDepartment.objects.get(data_source=full_local_data_source, code="group_aaa")
        group_aba = DataSourceDepartment.objects.get(data_source=full_local_data_source, code="group_aba")

        data_source_department_ids = [group_aaa.id, group_aba.id]

        result = TenantOrgPathHandler._query_org_path(data_source_department_ids, include_self=True)

        assert result[group_aaa.id] == "公司/部门A/中心AA/小组AAA"
        assert result[group_aba.id] == "公司/部门A/中心AB/小组ABA"

    def test_query_org_path_exclude_self(self, full_local_data_source):
        """测试不包含自身的组织路径"""
        group_aaa = DataSourceDepartment.objects.get(data_source=full_local_data_source, code="group_aaa")
        center_ab = DataSourceDepartment.objects.get(data_source=full_local_data_source, code="center_ab")

        data_source_department_ids = [group_aaa.id, center_ab.id]

        result = TenantOrgPathHandler._query_org_path(data_source_department_ids, include_self=False)

        assert result[group_aaa.id] == "公司/部门A/中心AA"
        assert result[center_ab.id] == "公司/部门A"

    def test_query_org_path_root_department(self, full_local_data_source):
        """测试根部门的组织路径"""
        company = DataSourceDepartment.objects.get(data_source=full_local_data_source, code="company")

        data_source_department_ids = [company.id]

        result = TenantOrgPathHandler._query_org_path(data_source_department_ids, include_self=True)

        assert result[company.id] == "公司"

    def test_query_org_path_with_empty_input(self):
        """测试空输入"""
        data_source_department_ids: List[int] = []
        result = TenantOrgPathHandler._query_org_path(data_source_department_ids, include_self=True)
        assert result == {}
