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

import datetime
from typing import Any
from unittest.mock import patch

import pytest
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceSensitiveInfo,
    DataSourceUser,
    LocalDataSourceIdentityInfo,
)
from bkuser.apps.idp.constants import IdpStatus
from bkuser.apps.idp.models import Idp, IdpDataSourceRelation
from bkuser.apps.tenant.models import TenantManager, TenantUser
from bkuser.biz.data_source import DataSourceHandler
from bkuser.biz.idp_data_source import IdpDataSourceRelationHandler
from bkuser.biz.tenant import RealLocalIdentityConfig, RealLocalIdentityInitError, RealLocalIdentityInitializer
from bkuser.common.hashers import make_password
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.idp_plugins.local.plugin import LocalIdpPluginConfig
from bkuser.plugins.base import get_default_plugin_cfg
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.constants import PasswordGenerateMethod
from django.db import IntegrityError
from django.utils import timezone
from pydantic import ValidationError

pytestmark = pytest.mark.django_db

ADMIN_PASSWORD = "Passwd-123456!"
NEW_USER_PASSWORD = "NewUser-654321!"


def _initialize(tenant_id: str, **kwargs) -> bool:
    config = RealLocalIdentityConfig(username="manager", password=ADMIN_PASSWORD, **kwargs)
    return RealLocalIdentityInitializer(tenant_id, config).initialize()


@pytest.mark.parametrize("username", ["yanshou", "yan.shou", "yan_shou-1", "a1"])
def test_config_accepts_valid_username(username):
    assert RealLocalIdentityConfig(username=username, password=ADMIN_PASSWORD).username == username


@pytest.mark.parametrize("username", ["", "a", "yan shou", "yanshou@corp", "_yanshou", "yanshou-", "a" * 33])
def test_config_rejects_invalid_username(username):
    with pytest.raises(ValidationError, match="username"):
        RealLocalIdentityConfig(username=username, password=ADMIN_PASSWORD)


def test_config_rejects_empty_admin_password():
    with pytest.raises(ValidationError, match="password is required"):
        RealLocalIdentityConfig(username="manager", password="")


def test_config_requires_new_user_fixed_password_when_method_is_fixed():
    with pytest.raises(ValidationError, match="new_user_fixed_password is required"):
        RealLocalIdentityConfig(
            username="manager", password=ADMIN_PASSWORD, new_user_password_method=PasswordGenerateMethod.FIXED
        )


def test_config_rejects_new_user_fixed_password_when_method_is_random():
    with pytest.raises(ValidationError, match="only allowed"):
        RealLocalIdentityConfig(username="manager", password=ADMIN_PASSWORD, new_user_fixed_password=NEW_USER_PASSWORD)


@pytest.mark.parametrize("password", ["weak", "bluking@2025"])
def test_initialize_rejects_weak_admin_password(default_tenant, password):
    config = RealLocalIdentityConfig(username="manager", password=password)
    with pytest.raises(RealLocalIdentityInitError, match="password does not satisfy"):
        RealLocalIdentityInitializer(default_tenant.id, config).initialize()

    assert not DataSource.objects.filter(owner_tenant_id=default_tenant.id, type=DataSourceTypeEnum.REAL).exists()


def test_initialize_rejects_weak_new_user_fixed_password(default_tenant):
    with pytest.raises(RealLocalIdentityInitError, match="固定密码的值不符合密码规则"):
        _initialize(
            default_tenant.id,
            new_user_password_method=PasswordGenerateMethod.FIXED,
            new_user_fixed_password="weak",
        )

    assert not DataSource.objects.filter(owner_tenant_id=default_tenant.id, type=DataSourceTypeEnum.REAL).exists()


def test_initialize_requires_existing_tenant():
    with pytest.raises(RealLocalIdentityInitError, match="does not exist"):
        _initialize("not-exists")


def test_initialize_creates_real_local_identity(default_tenant):
    assert _initialize(default_tenant.id) is True

    data_source = DataSource.objects.get(owner_tenant_id=default_tenant.id, name="本地数据源")
    assert data_source.type == DataSourceTypeEnum.REAL
    assert data_source.plugin_id == DataSourcePluginEnum.LOCAL

    # 默认新增用户使用随机初始密码，除启用账密登录外与页面新建本地数据源的默认配置一致
    plugin_config = data_source.get_plugin_cfg()
    assert plugin_config.enable_password is True
    default_config = get_default_plugin_cfg(DataSourcePluginEnum.LOCAL)
    assert plugin_config.model_dump(exclude={"enable_password"}) == default_config.model_dump(
        exclude={"enable_password"}
    )
    assert plugin_config.password_initial.generate_method == PasswordGenerateMethod.RANDOM

    idp = Idp.objects.get(owner_tenant_id=default_tenant.id, name="账密登录")
    assert idp.status == IdpStatus.ENABLED
    assert idp.plugin_id == BuiltinIdpPluginEnum.LOCAL
    assert idp.get_plugin_cfg().data_source_ids == [data_source.id]
    assert IdpDataSourceRelation.objects.filter(idp=idp, data_source=data_source).exists()

    tenant_user = TenantUser.objects.get(
        tenant=default_tenant,
        data_source=data_source,
        data_source_user__username="manager",
    )
    identity = LocalDataSourceIdentityInfo.objects.get(user=tenant_user.data_source_user)
    assert identity.check_password(ADMIN_PASSWORD)
    expected_expired_at = timezone.now() + datetime.timedelta(days=plugin_config.password_expire.valid_time)
    assert abs(identity.password_expired_at - expected_expired_at) < datetime.timedelta(minutes=1)
    assert TenantManager.objects.filter(tenant=default_tenant, tenant_user=tenant_user).exists()


def test_initialize_with_fixed_new_user_password_keeps_admin_password(default_tenant):
    assert (
        _initialize(
            default_tenant.id,
            new_user_password_method=PasswordGenerateMethod.FIXED,
            new_user_fixed_password=NEW_USER_PASSWORD,
        )
        is True
    )

    data_source = DataSource.objects.get(owner_tenant_id=default_tenant.id, type=DataSourceTypeEnum.REAL)
    plugin_config = data_source.get_plugin_cfg()
    assert plugin_config.password_initial.generate_method == PasswordGenerateMethod.FIXED
    assert plugin_config.password_initial.fixed_password == NEW_USER_PASSWORD
    default_config = get_default_plugin_cfg(DataSourcePluginEnum.LOCAL)
    excluded: dict[str, Any] = {"enable_password": True, "password_initial": {"generate_method", "fixed_password"}}
    assert plugin_config.model_dump(exclude=excluded) == default_config.model_dump(exclude=excluded)
    assert (
        DataSourceSensitiveInfo.objects.get(data_source=data_source, key="password_initial.fixed_password").value
        == NEW_USER_PASSWORD
    )

    identity = LocalDataSourceIdentityInfo.objects.get(data_source=data_source, username="manager")
    assert identity.check_password(ADMIN_PASSWORD)
    assert not identity.check_password(NEW_USER_PASSWORD)


def test_initialize_is_idempotent(default_tenant):
    assert _initialize(default_tenant.id) is True
    assert _initialize(default_tenant.id) is False
    assert DataSource.objects.filter(owner_tenant_id=default_tenant.id, type=DataSourceTypeEnum.REAL).count() == 1


def test_initialize_skips_after_manager_changed_password(default_tenant):
    _initialize(default_tenant.id)
    identity = LocalDataSourceIdentityInfo.objects.get(username="manager")
    identity.password = make_password("Changed-12345!")
    identity.save(update_fields=["password"])

    assert _initialize(default_tenant.id) is False

    identity.refresh_from_db()
    assert identity.check_password("Changed-12345!")


def test_initialize_skips_when_real_local_data_source_exists(default_tenant):
    DataSource.objects.create(
        owner_tenant_id=default_tenant.id,
        name="运维手工创建",
        type=DataSourceTypeEnum.REAL,
        plugin_id=DataSourcePluginEnum.LOCAL,
        plugin_config=get_default_plugin_cfg(DataSourcePluginEnum.LOCAL),
    )

    assert _initialize(default_tenant.id) is False
    assert not DataSource.objects.filter(owner_tenant_id=default_tenant.id, name="本地数据源").exists()
    assert not DataSourceUser.objects.filter(username="manager").exists()


def test_initialize_skips_when_orphan_local_idp_exists(default_tenant):
    _initialize(default_tenant.id)

    # 模拟页面删除实名数据源：仅删除关联关系，认证源保留为孤儿态
    data_source = DataSource.objects.get(owner_tenant_id=default_tenant.id, type=DataSourceTypeEnum.REAL)
    IdpDataSourceRelationHandler.remove_data_source_relations(data_source)
    DataSourceHandler.delete_data_source_and_related_resources(data_source)
    orphan_idp = Idp.objects.get(owner_tenant_id=default_tenant.id, name="账密登录")

    assert _initialize(default_tenant.id) is False

    assert not DataSource.objects.filter(owner_tenant_id=default_tenant.id, type=DataSourceTypeEnum.REAL).exists()
    assert not DataSourceUser.objects.filter(username="manager").exists()
    assert not IdpDataSourceRelation.objects.filter(idp=orphan_idp).exists()


def test_initialize_skips_when_renamed_orphan_local_idp_exists(default_tenant):
    _initialize(default_tenant.id)

    data_source = DataSource.objects.get(owner_tenant_id=default_tenant.id, type=DataSourceTypeEnum.REAL)
    IdpDataSourceRelationHandler.remove_data_source_relations(data_source)
    DataSourceHandler.delete_data_source_and_related_resources(data_source)
    orphan_idp = Idp.objects.get(owner_tenant_id=default_tenant.id, name="账密登录")
    orphan_idp.name = "本地账密"
    orphan_idp.save(update_fields=["name"])

    assert _initialize(default_tenant.id) is False

    assert not DataSource.objects.filter(owner_tenant_id=default_tenant.id, type=DataSourceTypeEnum.REAL).exists()
    assert Idp.objects.filter(owner_tenant_id=default_tenant.id, plugin_id=BuiltinIdpPluginEnum.LOCAL).count() == 2
    idp = Idp.objects.get(id=orphan_idp.id)
    assert idp.name == "本地账密"
    assert not IdpDataSourceRelation.objects.filter(idp=idp).exists()


def test_initialize_rolls_back_when_idp_name_conflicts(default_tenant):
    builtin_data_source = DataSource.objects.get(
        owner_tenant_id=default_tenant.id, type=DataSourceTypeEnum.BUILTIN_MANAGEMENT
    )
    idp = Idp.objects.create(
        owner_tenant_id=default_tenant.id,
        name="账密登录",
        plugin_id=BuiltinIdpPluginEnum.LOCAL,
        plugin_config=LocalIdpPluginConfig(data_source_ids=[builtin_data_source.id]),
    )
    IdpDataSourceRelation.objects.create(
        idp=idp, data_source=builtin_data_source, idp_owner_tenant_id=default_tenant.id
    )

    with pytest.raises(IntegrityError):
        _initialize(default_tenant.id)

    assert not DataSource.objects.filter(owner_tenant_id=default_tenant.id, type=DataSourceTypeEnum.REAL).exists()
    assert list(IdpDataSourceRelation.objects.filter(idp=idp).values_list("data_source_id", flat=True)) == [
        builtin_data_source.id
    ]


def test_initialize_rolls_back_on_failure(default_tenant):
    with (
        patch.object(TenantManager.objects, "create", side_effect=RuntimeError("boom")),
        pytest.raises(RuntimeError, match="boom"),
    ):
        _initialize(default_tenant.id)

    assert not DataSource.objects.filter(owner_tenant_id=default_tenant.id, type=DataSourceTypeEnum.REAL).exists()
    assert not DataSourceUser.objects.filter(username="manager").exists()
