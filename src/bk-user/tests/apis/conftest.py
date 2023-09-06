# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import pytest
from bkuser.apps.data_source.constants import DataSourcePluginEnum
from bkuser.apps.data_source.models import DataSource
from rest_framework.test import APIClient

from tests.test_utils.helpers import generate_random_string


@pytest.fixture()
def api_client(bk_user) -> APIClient:
    """Return an authenticated client"""
    client = APIClient()
    client.force_authenticate(user=bk_user)
    return client


@pytest.fixture()
def local_data_source(default_tenant: str) -> DataSource:
    """
    生成测试数据源
    """

    local_data_source, _ = DataSource.objects.get_or_create(
        name=generate_random_string(),
        defaults={"owner_tenant_id": default_tenant, "plugin_id": DataSourcePluginEnum.LOCAL.value},
    )
    return local_data_source
