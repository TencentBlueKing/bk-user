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
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.tenant.models import TenantUser
from bkuser.apps.tenant.utils import TenantUserIDGenerator
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

pytestmark = pytest.mark.django_db


@pytest.fixture
def data_source_id():
    return 114514


@pytest.fixture
def valid_data():
    return {
        "username": "v_user",
        "full_name": "虚拟用户",
        "email": "v@example.com",
        "phone": "13800000000",
        "phone_country_code": "86",
        "app_codes": ["app1", "app2"],
        "owners": ["real_user"],
    }


@pytest.fixture
def create_real_owner():
    def _create(tenant_id, username="real_user"):
        data_source, _ = DataSource.objects.get_or_create(
            type=DataSourceTypeEnum.REAL,
            owner_tenant_id=tenant_id,
            defaults={
                "plugin_id": DataSourcePluginEnum.LOCAL,
                "plugin_config": LocalDataSourcePluginConfig(enable_password=False),
            },
        )
        ds_user = DataSourceUser.objects.create(
            username=username,
            data_source=data_source,
        )
        TenantUser.objects.create(
            id=TenantUserIDGenerator(tenant_id, data_source).gen(ds_user),
            data_source=data_source,
            tenant_id=tenant_id,
            data_source_user=ds_user,
        )

    return _create
