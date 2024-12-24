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
from unittest import mock

import pytest
from bkuser.apis.apigw.authentications import InterBearerToken
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.tenant.constants import TenantUserIdRuleEnum
from bkuser.apps.tenant.models import TenantUserIDGenerateConfig
from bkuser.plugins.local.models import LocalDataSourcePluginConfig
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIClient

from tests.test_utils.data_source import init_data_source_users_depts_and_relations
from tests.test_utils.tenant import sync_users_depts_to_tenant


def mock_token_authenticate(self, request):
    request.inter_bearer_token = InterBearerToken(verified=True)
    return AnonymousUser(), None


@pytest.fixture
def apigw_api_client() -> APIClient:
    client = APIClient()

    with mock.patch(
        "bkuser.apis.apigw.authentications.InnerBearerTokenAuthentication.authenticate", new=mock_token_authenticate
    ):
        yield client


@pytest.fixture
def default_tenant_user_data(default_tenant, local_ds_plugin_cfg, local_ds_plugin) -> DataSource:
    """默认租户的本地数据源数据"""
    data_source = DataSource.objects.create(
        owner_tenant_id=default_tenant.id,
        type=DataSourceTypeEnum.REAL,
        plugin=local_ds_plugin,
        plugin_config=LocalDataSourcePluginConfig(**local_ds_plugin_cfg),
    )
    init_data_source_users_depts_and_relations(data_source)

    # 设置租户用户生成规则表，让 tenant_user_id 与 数据源 username 一样
    TenantUserIDGenerateConfig.objects.create(
        data_source=data_source,
        target_tenant_id=default_tenant.id,
        rule=TenantUserIdRuleEnum.USERNAME,
    )

    sync_users_depts_to_tenant(default_tenant, data_source)
    return data_source
