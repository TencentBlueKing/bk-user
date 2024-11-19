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
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.sync.loggers import TaskLogger
from bkuser.apps.sync.validators import DataSourceUserExtrasUniqueValidator
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import TenantUserCustomField
from bkuser.plugins.constants import DataSourcePluginEnum

pytestmark = pytest.mark.django_db


class TestDataSourceUserExtrasUniqueValidator:
    """测试对有唯一性要求的自定义字段的校验"""

    @pytest.fixture
    def logger(self) -> TaskLogger:
        return TaskLogger()

    @pytest.fixture
    def tenant_user_custom_field(self, request) -> TenantUserCustomField:
        tenant = request.getfixturevalue("random_tenant")
        return TenantUserCustomField.objects.create(
            tenant=tenant,
            name="age",
            display_name="年龄",
            data_type=UserFieldDataType.NUMBER,
            required=False,
            unique=True,
            default=0,
        )

    @pytest.fixture
    def random_ds(self, request) -> DataSource:
        tenant_id = request.getfixturevalue("random_tenant").id
        ds, _ = DataSource.objects.get_or_create(owner_tenant_id=tenant_id, plugin_id=DataSourcePluginEnum.LOCAL)
        return ds

    @pytest.fixture
    def user_lisi(self, request) -> DataSourceUser:
        random_ds = request.getfixturevalue("random_ds")
        return DataSourceUser.objects.create(
            data_source=random_ds, username="lisi", full_name="李四", extras={"age": 20}
        )

    @pytest.fixture
    def user_wangwu(self, request) -> DataSourceUser:
        random_ds = request.getfixturevalue("random_ds")
        return DataSourceUser.objects.create(
            data_source=random_ds, username="wangwu", full_name="王五", extras={"age": 18}
        )

    def test_validate_without_custom_fields(self, random_tenant, random_ds, user_lisi, user_wangwu, logger):
        DataSourceUserExtrasUniqueValidator(random_ds, logger).validate()

    def test_validate_with_custom_fields(
        self, random_tenant, random_ds, user_lisi, user_wangwu, logger, tenant_user_custom_field
    ):
        DataSourceUserExtrasUniqueValidator(random_ds, logger).validate()

    def test_validate_with_duplicate_unique(
        self, random_tenant, random_ds, user_lisi, user_wangwu, logger, tenant_user_custom_field
    ):
        user_lisi.extras = {"age": 18}
        user_lisi.save()

        with pytest.raises(ValueError, match="duplicate unique values found"):
            DataSourceUserExtrasUniqueValidator(random_ds, logger).validate()
