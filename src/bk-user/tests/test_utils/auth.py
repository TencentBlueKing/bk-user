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
from bkuser.apps.tenant.models import Tenant, TenantManager, TenantUser
from bkuser.auth.models import User
from tests.test_utils.helpers import generate_random_string


def create_user(tenant: Tenant, username: Optional[str] = None) -> User:
    """创建测试用用户"""
    username = username or generate_random_string(length=8)
    user, _ = User.objects.get_or_create(username=username)
    user.set_property("tenant_id", tenant.id)

    # 获取租户默认的本地数据源
    data_source = DataSource.objects.get(owner_tenant_id=tenant.id, name=f"{tenant.id}-default-local")

    data_source_user, _ = DataSourceUser.objects.get_or_create(
        username=username,
        data_source=data_source,
        defaults={
            "full_name": username,
            "email": f"{username}@qq.com",
            "phone": "13123456789",
        },
    )

    tenant_user, _ = TenantUser.objects.get_or_create(
        tenant=tenant,
        id=username,
        data_source=data_source,
        data_source_user=data_source_user,
    )

    TenantManager.objects.get_or_create(tenant=tenant, tenant_user=tenant_user)

    return user
