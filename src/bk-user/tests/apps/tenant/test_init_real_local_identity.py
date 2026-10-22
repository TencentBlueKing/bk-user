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

import pytest
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, LocalDataSourceIdentityInfo
from bkuser.plugins.local.constants import PasswordGenerateMethod
from django.core.management import CommandError, call_command
from django.test import override_settings

pytestmark = pytest.mark.django_db

ADMIN_PASSWORD = "Passwd-123456!"
NEW_USER_PASSWORD = "NewUser-654321!"


def _call(**options) -> str:
    out = StringIO()
    call_command("init_real_local_identity", stdout=out, stderr=StringIO(), **options)
    return out.getvalue()


def _has_real_local_data_source(tenant_id: str) -> bool:
    return DataSource.objects.filter(
        owner_tenant_id=tenant_id, type=DataSourceTypeEnum.REAL, plugin_id="local"
    ).exists()


@override_settings(ENABLE_MULTI_TENANT_MODE=False)
def test_single_tenant_mode_initializes_default_tenant(default_tenant):
    output = _call(username="manager", password=ADMIN_PASSWORD)

    assert "successfully" in output
    assert _has_real_local_data_source(default_tenant.id)


@override_settings(ENABLE_MULTI_TENANT_MODE=False)
def test_single_tenant_mode_ignores_tenant_id(default_tenant, random_tenant):
    _call(tenant_id=random_tenant.id, username="manager", password=ADMIN_PASSWORD)

    assert _has_real_local_data_source(default_tenant.id)
    assert not _has_real_local_data_source(random_tenant.id)


@override_settings(ENABLE_MULTI_TENANT_MODE=True)
def test_multi_tenant_mode_requires_tenant_id(default_tenant):
    with pytest.raises(CommandError, match="tenant_id is required"):
        _call(username="manager", password=ADMIN_PASSWORD)

    assert not _has_real_local_data_source(default_tenant.id)


@override_settings(ENABLE_MULTI_TENANT_MODE=True)
def test_multi_tenant_mode_initializes_specified_tenant(default_tenant, random_tenant):
    _call(tenant_id=random_tenant.id, username="manager", password=ADMIN_PASSWORD)

    assert _has_real_local_data_source(random_tenant.id)
    assert not _has_real_local_data_source(default_tenant.id)


@override_settings(ENABLE_MULTI_TENANT_MODE=True)
def test_rejects_not_exists_tenant():
    with pytest.raises(CommandError, match="does not exist"):
        _call(tenant_id="not-exists", username="manager", password=ADMIN_PASSWORD)


def test_rejects_weak_admin_password(default_tenant):
    with pytest.raises(CommandError, match="password does not satisfy"):
        _call(tenant_id=default_tenant.id, username="manager", password="bluking@2025")

    assert not _has_real_local_data_source(default_tenant.id)


def test_fixed_method_requires_new_user_fixed_password(default_tenant):
    with pytest.raises(CommandError, match="new_user_fixed_password is required"):
        _call(
            tenant_id=default_tenant.id,
            username="manager",
            password=ADMIN_PASSWORD,
            new_user_password_method=PasswordGenerateMethod.FIXED,
        )

    assert not _has_real_local_data_source(default_tenant.id)


def test_fixed_method_sets_new_user_password_and_keeps_admin_password(default_tenant):
    _call(
        tenant_id=default_tenant.id,
        username="manager",
        password=ADMIN_PASSWORD,
        new_user_password_method=PasswordGenerateMethod.FIXED,
        new_user_fixed_password=NEW_USER_PASSWORD,
    )

    data_source = DataSource.objects.get(owner_tenant_id=default_tenant.id, type=DataSourceTypeEnum.REAL)
    assert data_source.get_plugin_cfg().password_initial.fixed_password == NEW_USER_PASSWORD
    identity = LocalDataSourceIdentityInfo.objects.get(data_source=data_source, username="manager")
    assert identity.check_password(ADMIN_PASSWORD)


def test_skips_when_already_initialized(default_tenant):
    _call(tenant_id=default_tenant.id, username="manager", password=ADMIN_PASSWORD)

    output = _call(tenant_id=default_tenant.id, username="manager", password=ADMIN_PASSWORD)

    assert "skip" in output
    assert DataSource.objects.filter(owner_tenant_id=default_tenant.id, type=DataSourceTypeEnum.REAL).count() == 1
