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
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.auth.models import User

from tests.test_utils.auth import create_user
from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import create_tenant


@pytest.fixture()
def default_tenant() -> str:
    """初始化默认租户"""
    return create_tenant().id


@pytest.fixture()
def random_tenant() -> str:
    """生成随机租户"""
    return create_tenant(generate_random_string()).id


@pytest.fixture()
def default_data_source(default_tenant) -> DataSource:
    # 支持检查是否使用 random_tenant fixture 以生成不属于默认租户的数据源
    return DataSource.objects.create(
        name=generate_random_string(),
        owner_tenant_id=default_tenant,
        plugin_id=DataSourcePluginEnum.LOCAL,
    )


@pytest.fixture()
def bk_user(default_data_source) -> User:
    """生成随机用户"""
    user = create_user()

    # 补充数据源信息
    data_source_user, _ = DataSourceUser.objects.get_or_create(
        full_name=generate_random_string(),
        username=user.username,
        email=f"{generate_random_string()}@qq.com",
        phone="13123456789",
        data_source=default_data_source,
    )
    return user
