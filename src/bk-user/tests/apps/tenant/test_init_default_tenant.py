# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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

from io import StringIO
from typing import Dict

import pytest
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.tenant.constants import BuiltInTenantIDEnum
from bkuser.apps.tenant.models import TenantUser
from django.core.management import call_command
from django.test import override_settings

pytestmark = pytest.mark.django_db

ADMIN_PASSWORD = "Passwd-123456!"


def _call():
    call_command("init_default_tenant", stdout=StringIO(), stderr=StringIO())


def _virtual_users(tenant_id: str) -> Dict[str, str]:
    """返回 {username: tenant_user_id}"""
    return dict(
        TenantUser.objects.filter(tenant_id=tenant_id, data_source__type=DataSourceTypeEnum.VIRTUAL).values_list(
            "data_source_user__username", "id"
        )
    )


@override_settings(ENABLE_MULTI_TENANT_MODE=True, INITIAL_ADMIN_PASSWORD=ADMIN_PASSWORD)
def test_default_bk_admin_username():
    _call()

    assert set(_virtual_users(BuiltInTenantIDEnum.SYSTEM)) == {"bk_admin"}


@override_settings(ENABLE_MULTI_TENANT_MODE=True, INITIAL_ADMIN_PASSWORD=ADMIN_PASSWORD, BK_ADMIN_USERNAME="bk_ops")
def test_custom_bk_admin_username():
    _call()

    assert set(_virtual_users(BuiltInTenantIDEnum.SYSTEM)) == {"bk_ops"}


@override_settings(ENABLE_MULTI_TENANT_MODE=False, INITIAL_ADMIN_PASSWORD=ADMIN_PASSWORD, BK_ADMIN_USERNAME="bk_ops")
def test_single_tenant_mode_keeps_legacy_admin():
    _call()

    vusers = _virtual_users(BuiltInTenantIDEnum.DEFAULT)
    assert set(vusers) == {"bk_ops", "admin"}
    assert vusers["admin"] == "admin"


@override_settings(ENABLE_MULTI_TENANT_MODE=False, INITIAL_ADMIN_PASSWORD=ADMIN_PASSWORD, BK_ADMIN_USERNAME="admin")
def test_single_tenant_mode_dedup_legacy_admin():
    _call()

    assert _virtual_users(BuiltInTenantIDEnum.DEFAULT) == {"admin": "admin"}


@override_settings(ENABLE_MULTI_TENANT_MODE=True, INITIAL_ADMIN_PASSWORD=ADMIN_PASSWORD)
def test_rerun_only_creates_new_username():
    _call()
    with override_settings(BK_ADMIN_USERNAME="bk_ops"):
        _call()

    assert set(_virtual_users(BuiltInTenantIDEnum.SYSTEM)) == {"bk_admin", "bk_ops"}
