# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import pytest
from bkuser.apps.data_source.models import DataSourceDepartment, DataSourceUser
from bkuser.apps.tenant.constants import TenantUserIdRuleEnum
from bkuser.apps.tenant.models import TenantDepartmentIDRecord, TenantUserIDGenerateConfig, TenantUserIDRecord
from bkuser.apps.tenant.utils import TenantDeptIDGenerator, TenantUserIDGenerator
from bkuser.utils.uuid import generate_uuid

pytestmark = pytest.mark.django_db


@pytest.fixture()
def zhangsan(full_local_data_source) -> DataSourceUser:
    return DataSourceUser.objects.filter(data_source=full_local_data_source, username="zhangsan").first()


@pytest.fixture()
def lisi(full_local_data_source) -> DataSourceUser:
    return DataSourceUser.objects.filter(data_source=full_local_data_source, username="lisi").first()


class TestTenantUserIdGenerator:
    """测试租户用户 ID 生成器"""

    def test_gen_by_username(self, random_tenant, full_local_data_source, zhangsan):
        TenantUserIDGenerateConfig.objects.create(
            data_source=full_local_data_source, target_tenant=random_tenant, rule=TenantUserIdRuleEnum.USERNAME
        )
        user_id = TenantUserIDGenerator(random_tenant.id, full_local_data_source).gen(zhangsan)
        assert user_id == "zhangsan"

    def test_gen_by_username_and_domain(self, random_tenant, full_local_data_source, zhangsan):
        TenantUserIDGenerateConfig.objects.create(
            data_source=full_local_data_source,
            target_tenant=random_tenant,
            rule=TenantUserIdRuleEnum.USERNAME_WITH_DOMAIN,
            domain="bk.example.com",
        )
        user_id = TenantUserIDGenerator(random_tenant.id, full_local_data_source).gen(zhangsan)
        assert user_id == "zhangsan@bk.example.com"

    def test_gen_single_uuid_with_record(self, random_tenant, full_local_data_source, zhangsan):
        uuid = generate_uuid()
        TenantUserIDRecord.objects.create(
            tenant_id=random_tenant.id, data_source=full_local_data_source, code=zhangsan.code, tenant_user_id=uuid
        )

        generator = TenantUserIDGenerator(random_tenant.id, full_local_data_source)
        assert generator.gen(zhangsan) == uuid
        assert generator.tenant_user_id_map == {}

    def test_gen_single_uuid_without_record(self, random_tenant, full_local_data_source, zhangsan):
        generator = TenantUserIDGenerator(random_tenant.id, full_local_data_source)
        assert len(generator.gen(zhangsan)) == 32
        assert generator.tenant_user_id_map == {}

    def test_gen_multi_uuid_with_records(self, random_tenant, full_local_data_source, zhangsan, lisi):
        uuid = generate_uuid()
        TenantUserIDRecord.objects.create(
            tenant_id=random_tenant.id, data_source=full_local_data_source, code=zhangsan.code, tenant_user_id=uuid
        )

        generator = TenantUserIDGenerator(random_tenant.id, full_local_data_source, prepare_batch=True)
        assert generator.gen(zhangsan) == uuid
        assert len(generator.gen(lisi)) == 32
        assert len(generator.tenant_user_id_map) == 1
        assert TenantUserIDRecord.objects.filter(data_source=full_local_data_source).count() == 2

    def test_gen_multi_uuid_without_records(self, random_tenant, full_local_data_source, zhangsan, lisi):
        generator = TenantUserIDGenerator(random_tenant.id, full_local_data_source, prepare_batch=True)
        assert len(generator.gen(zhangsan)) == 32
        assert len(generator.gen(lisi)) == 32
        assert len(generator.tenant_user_id_map) == 0
        assert TenantUserIDRecord.objects.filter(data_source=full_local_data_source).count() == 2


@pytest.fixture()
def company(full_local_data_source) -> DataSourceDepartment:
    return DataSourceDepartment.objects.filter(data_source=full_local_data_source, code="company").first()


@pytest.fixture()
def dept_a(full_local_data_source) -> DataSourceDepartment:
    return DataSourceDepartment.objects.filter(data_source=full_local_data_source, code="dept_a").first()


class TestTenantDeptIdGenerator:
    """测试租户用户 ID 生成器"""

    def test_gen_single_with_record(self, random_tenant, full_local_data_source, company):
        TenantDepartmentIDRecord.objects.create(
            tenant_id=random_tenant.id,
            data_source=full_local_data_source,
            code=company.code,
            tenant_department_id=100,
        )

        generator = TenantDeptIDGenerator(random_tenant.id, full_local_data_source)
        assert generator.gen(company) == 100
        assert generator.tenant_dept_id_map == {}

    def test_gen_single_without_record(self, random_tenant, full_local_data_source, company):
        # 没有历史记录，返回 None，由 DB 生成自增 ID
        generator = TenantDeptIDGenerator(random_tenant.id, full_local_data_source)
        assert generator.gen(company) is None

    def test_gen_multi_with_records(self, random_tenant, full_local_data_source, company, dept_a):
        TenantDepartmentIDRecord.objects.create(
            tenant_id=random_tenant.id,
            data_source=full_local_data_source,
            code=company.code,
            tenant_department_id=101,
        )

        generator = TenantDeptIDGenerator(random_tenant.id, full_local_data_source, prepare_batch=True)
        assert generator.gen(company) == 101
        assert generator.gen(dept_a) is None
        assert len(generator.tenant_dept_id_map) == 1

    def test_gen_multi_without_records(self, random_tenant, full_local_data_source, company, dept_a):
        generator = TenantDeptIDGenerator(random_tenant.id, full_local_data_source, prepare_batch=True)
        assert generator.gen(company) is None
        assert generator.gen(dept_a) is None
        assert len(generator.tenant_dept_id_map) == 0
