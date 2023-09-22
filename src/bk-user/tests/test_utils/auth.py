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

from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.models import TenantUser
from bkuser.auth.models import User
from bkuser.utils.uuid import generate_uuid
from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import DEFAULT_TENANT


def create_user(username: Optional[str] = None) -> User:
    """创建测试用用户"""
    username = username or generate_random_string(length=8)
    user, _ = User.objects.get_or_create(username=username)
    return user


def set_tenant_user(user: User, data_source_id: int, tenant: Optional[str] = DEFAULT_TENANT) -> str:
    """
    设置测试用户租户信息
    """
    data_source_user = DataSourceUser.objects.get(username=user.username, data_source_id=data_source_id)

    tenant_user = TenantUser.objects.create(
        data_source_user=data_source_user, tenant_id=tenant, data_source_id=data_source_id, id=generate_uuid()
    )
    user.set_property("bk_username", tenant_user.id)
    user.set_property("tenant_id", tenant)

    return tenant_user.id
