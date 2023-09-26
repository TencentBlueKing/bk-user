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
from rest_framework.test import APIClient

from tests.test_utils.auth import set_tenant_user


@pytest.fixture()
def api_client(bk_user, default_tenant, default_data_source) -> APIClient:
    """Return an authenticated client"""
    client = APIClient()
    set_tenant_user(bk_user, default_data_source.id, default_tenant.id)
    client.force_authenticate(user=bk_user)
    return client
