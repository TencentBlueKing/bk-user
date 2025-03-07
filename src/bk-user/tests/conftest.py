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
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.sync.handlers import (
    set_data_source_sync_periodic_task,
    sync_identity_infos_and_notify_after_modify_data_source,
)
from bkuser.apps.tenant.models import Tenant
from bkuser.auth.models import User
from django.db.models.signals import post_save

from tests.fixtures.data_source import (  # noqa: F401
    bare_general_data_source,
    bare_local_data_source,
    bare_virtual_data_source,
    full_general_data_source,
    full_local_data_source,
    full_virtual_data_source,
    general_ds_plugin,
    general_ds_plugin_cfg,
    ldap_ds_plugin_cfg,
    local_ds_plugin,
    local_ds_plugin_cfg,
)
from tests.fixtures.tenant import tenant_user_custom_fields  # noqa: F401
from tests.test_utils.auth import create_user
from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import create_tenant

# 在单元测试中屏蔽掉 post_save 信号的触发
post_save.disconnect(set_data_source_sync_periodic_task, sender=DataSource)
post_save.disconnect(sync_identity_infos_and_notify_after_modify_data_source, sender=DataSource)


@pytest.fixture
def default_tenant() -> Tenant:
    """初始化默认租户"""
    return create_tenant()


@pytest.fixture
def random_tenant() -> Tenant:
    """生成随机租户"""
    return create_tenant(generate_random_string())


@pytest.fixture
def bk_user(request, default_tenant) -> User:
    """生成随机用户"""
    tenant = default_tenant
    if "random_tenant" in request.fixturenames:
        tenant = request.getfixturevalue("random_tenant")

    return create_user(tenant)
