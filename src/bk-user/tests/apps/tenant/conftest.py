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
from datetime import timedelta

import pytest
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.tenant.constants import TenantUserStatus
from bkuser.apps.tenant.models import TenantUser
from bkuser.utils.time import get_midnight
from django.utils import timezone

from tests.test_utils.helpers import generate_random_string


@pytest.fixture
def not_expired_tenant_user(bare_local_data_source, random_tenant):
    data_source_user = DataSourceUser.objects.create(
        username=generate_random_string(length=8),
        full_name=generate_random_string(length=8),
        data_source=bare_local_data_source,
    )
    return TenantUser.objects.create(
        id=generate_random_string(),
        tenant=random_tenant,
        data_source=bare_local_data_source,
        data_source_user=data_source_user,
        status=TenantUserStatus.ENABLED,
        account_expired_at=timezone.now() + timedelta(days=1),
    )


@pytest.fixture
def expired_tenant_user(bare_local_data_source, random_tenant):
    data_source_user = DataSourceUser.objects.create(
        username=generate_random_string(length=8),
        full_name=generate_random_string(length=8),
        data_source=bare_local_data_source,
    )
    return TenantUser.objects.create(
        id=generate_random_string(),
        tenant=random_tenant,
        data_source=bare_local_data_source,
        data_source_user=data_source_user,
        status=TenantUserStatus.ENABLED,
        account_expired_at=get_midnight() - timedelta(days=1),
    )
