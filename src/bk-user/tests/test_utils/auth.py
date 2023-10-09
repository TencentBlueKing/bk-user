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

from typing import Optional

from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.tenant.models import TenantUser
from bkuser.auth.models import User
from bkuser.plugins.constants import DataSourcePluginEnum
from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import DEFAULT_TENANT


def create_user(username: Optional[str] = None) -> User:
    """创建测试用用户"""
    username = username or generate_random_string(length=8)
    user, _ = User.objects.get_or_create(username=username)
    user.set_property("tenant_id", DEFAULT_TENANT)

    # 补充数据源用户/租户用户信息
    data_source, _ = DataSource.objects.get_or_create(
        owner_tenant_id=DEFAULT_TENANT, plugin_id=DataSourcePluginEnum.LOCAL, name=generate_random_string()
    )

    random_string = generate_random_string()
    data_source_user, _ = DataSourceUser.objects.get_or_create(
        username=username,
        data_source_id=data_source.id,
        defaults={
            "full_name": random_string,
            "email": f"{random_string}@qq.com",
            "phone": "13123456789",
        },
    )

    TenantUser.objects.get_or_create(
        data_source_user=data_source_user, tenant_id=DEFAULT_TENANT, data_source_id=data_source.id, id=username
    )

    return user
