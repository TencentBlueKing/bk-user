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
from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import DEFAULT_TENANT


def create_user(tenant: Optional[str] = DEFAULT_TENANT, username: Optional[str] = None) -> User:
    """创建测试用用户"""
    username = username or generate_random_string(length=8)
    user, _ = User.objects.get_or_create(username=username)

    # 补充数据源，租户用户信息
    data_source = DataSource.objects.filter(
        owner_tenant_id=tenant,
    ).first()

    data_source_user, _ = DataSourceUser.objects.get_or_create(
        full_name=generate_random_string(),
        username=user.username,
        email=f"{generate_random_string()}@qq.com",
        phone="13123456789",
        data_source_id=data_source.id,
    )

    TenantUser.objects.create(
        data_source_user=data_source_user, tenant_id=tenant, data_source_id=data_source.id, id=user.username
    )
    user.set_property("tenant_id", tenant)
    return user
