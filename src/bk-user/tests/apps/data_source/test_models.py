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
from bkuser.apps.data_source.models import DataSource, DataSourceSensitiveInfo
from bkuser.common.constants import SENSITIVE_MASK
from bkuser.plugins.local.constants import PasswordGenerateMethod
from bkuser.plugins.local.models import LocalDataSourcePluginConfig
from bkuser.utils.dictx import get_items

pytestmark = pytest.mark.django_db

FAKE_PASSWORD = "Pa-@-114514-2887"


@pytest.fixture()
def local_ds_with_sensitive(bare_local_data_source) -> DataSource:
    """包含敏感信息的本地数据源"""
    plugin_config = bare_local_data_source.plugin_config
    plugin_config["password_initial"]["generate_method"] = PasswordGenerateMethod.FIXED
    plugin_config["password_initial"]["fixed_password"] = FAKE_PASSWORD

    bare_local_data_source.set_plugin_cfg(LocalDataSourcePluginConfig(**plugin_config))
    return bare_local_data_source


def test_get_plugin_config(local_ds_with_sensitive):
    plugin_cfg = local_ds_with_sensitive.get_plugin_cfg()

    assert isinstance(plugin_cfg, LocalDataSourcePluginConfig)
    assert plugin_cfg.password_initial.fixed_password == FAKE_PASSWORD  # type: ignore


def test_set_plugin_config(local_ds_plugin_cfg, bare_local_data_source):
    """给没有敏感信息的设置下"""
    assert not DataSourceSensitiveInfo.objects.filter(data_source=bare_local_data_source).exists()

    plugin_cfg = LocalDataSourcePluginConfig(**local_ds_plugin_cfg)
    plugin_cfg.password_initial.generate_method = PasswordGenerateMethod.FIXED  # type: ignore
    plugin_cfg.password_initial.fixed_password = FAKE_PASSWORD  # type: ignore

    bare_local_data_source.set_plugin_cfg(plugin_cfg)
    assert get_items(bare_local_data_source.plugin_config, "password_initial.fixed_password") == SENSITIVE_MASK

    plugin_cfg = bare_local_data_source.get_plugin_cfg()
    assert plugin_cfg.password_initial.fixed_password == FAKE_PASSWORD  # type: ignore

    sensitive_info = DataSourceSensitiveInfo.objects.get(
        data_source=bare_local_data_source, key="password_initial.fixed_password"
    )
    assert sensitive_info.value == FAKE_PASSWORD


def test_set_plugin_config_with_replace(local_ds_with_sensitive):
    """已经有加密的敏感信息，替换更新"""
    plugin_cfg = local_ds_with_sensitive.get_plugin_cfg()
    plugin_cfg.password_initial.fixed_password = FAKE_PASSWORD[::-1]

    local_ds_with_sensitive.set_plugin_cfg(plugin_cfg)
    assert get_items(local_ds_with_sensitive.plugin_config, "password_initial.fixed_password") == SENSITIVE_MASK

    plugin_cfg = local_ds_with_sensitive.get_plugin_cfg()
    assert plugin_cfg.password_initial.fixed_password == FAKE_PASSWORD[::-1]

    sensitive_info = DataSourceSensitiveInfo.objects.get(
        data_source=local_ds_with_sensitive, key="password_initial.fixed_password"
    )
    assert sensitive_info.value == FAKE_PASSWORD[::-1]


def test_set_plugin_config_not_value(bare_local_data_source):
    plugin_cfg = LocalDataSourcePluginConfig(enable_account_password_login=False)

    bare_local_data_source.set_plugin_cfg(plugin_cfg)
    assert get_items(bare_local_data_source.plugin_config, "password_initial.fixed_password") is None


def test_set_plugin_config_empty_value(local_ds_plugin_cfg, bare_local_data_source):
    plugin_cfg = LocalDataSourcePluginConfig(**local_ds_plugin_cfg)
    # local_ds_plugin_cfg 本身 fixed_password 本身就是 None，这里修改别的字段，是为了验证真的更新
    plugin_cfg.password_initial.force_change_at_first_login = False  # type: ignore

    bare_local_data_source.set_plugin_cfg(plugin_cfg)
    assert get_items(bare_local_data_source.plugin_config, "password_initial.fixed_password") is None
    assert get_items(bare_local_data_source.plugin_config, "password_initial.force_change_at_first_login") is False
