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
from typing import Any, Dict

import pytest
from bkuser.apps.data_source.models import DataSource, DataSourcePlugin
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.general.models import GeneralDataSourcePluginConfig
from bkuser.plugins.local.constants import NotificationMethod, NotificationScene, PasswordGenerateMethod
from bkuser.plugins.local.models import LocalDataSourcePluginConfig
from tests.test_utils.data_source import init_data_source_users_depts_and_relations
from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import DEFAULT_TENANT


@pytest.fixture()
def local_ds_plugin_cfg() -> Dict[str, Any]:
    return {
        "enable_account_password_login": True,
        "password_rule": {
            "min_length": 12,
            "contain_lowercase": True,
            "contain_uppercase": True,
            "contain_digit": True,
            "contain_punctuation": True,
            "not_continuous_count": 5,
            "not_keyboard_order": True,
            "not_continuous_letter": True,
            "not_continuous_digit": True,
            "not_repeated_symbol": True,
            "valid_time": 7,
            "max_retries": 3,
            "lock_time": 3600,
        },
        "password_initial": {
            "force_change_at_first_login": True,
            "cannot_use_previous_password": True,
            "reserved_previous_password_count": 3,
            "generate_method": PasswordGenerateMethod.RANDOM,
            "fixed_password": None,
            "notification": {
                "enabled_methods": [NotificationMethod.EMAIL, NotificationMethod.SMS],
                "templates": [
                    {
                        "method": NotificationMethod.EMAIL,
                        "scene": NotificationScene.USER_INITIALIZE,
                        "title": "您的账户已经成功创建",
                        "sender": "蓝鲸智云",
                        "content": "您的账户已经成功创建，请尽快修改密码",
                        "content_html": "<p>您的账户已经成功创建，请尽快修改密码</p>",
                    },
                    {
                        "method": NotificationMethod.EMAIL,
                        "scene": NotificationScene.RESET_PASSWORD,
                        "title": "登录密码重置",
                        "sender": "蓝鲸智云",
                        "content": "点击以下链接以重置代码",
                        "content_html": "<p>点击以下链接以重置代码</p>",
                    },
                    {
                        "method": NotificationMethod.SMS,
                        "scene": NotificationScene.USER_INITIALIZE,
                        "sender": "蓝鲸智云",
                        "content": "您的账户已经成功创建，请尽快修改密码",
                        "content_html": "<p>您的账户已经成功创建，请尽快修改密码</p>",
                    },
                    {
                        "method": NotificationMethod.SMS,
                        "scene": NotificationScene.RESET_PASSWORD,
                        "sender": "蓝鲸智云",
                        "content": "点击以下链接以重置代码",
                        "content_html": "<p>点击以下链接以重置代码</p>",
                    },
                ],
            },
        },
        "password_expire": {
            "remind_before_expire": [1, 7],
            "notification": {
                "enabled_methods": [NotificationMethod.EMAIL, NotificationMethod.SMS],
                "templates": [
                    {
                        "method": NotificationMethod.EMAIL,
                        "scene": NotificationScene.PASSWORD_EXPIRING,
                        "title": "【蓝鲸智云】密码即将到期提醒！",
                        "sender": "蓝鲸智云",
                        "content": "您的密码即将到期！",
                        "content_html": "<p>您的密码即将到期！</p>",
                    },
                    {
                        "method": NotificationMethod.EMAIL,
                        "scene": NotificationScene.PASSWORD_EXPIRED,
                        "title": "【蓝鲸智云】密码到期提醒！",
                        "sender": "蓝鲸智云",
                        "content": "点击以下链接以重置代码",
                        "content_html": "<p>您的密码已到期！</p>",
                    },
                    {
                        "method": NotificationMethod.SMS,
                        "scene": NotificationScene.PASSWORD_EXPIRING,
                        "sender": "蓝鲸智云",
                        "content": "您的密码即将到期！",
                        "content_html": "<p>您的密码即将到期！</p>",
                    },
                    {
                        "method": NotificationMethod.SMS,
                        "scene": NotificationScene.PASSWORD_EXPIRED,
                        "sender": "蓝鲸智云",
                        "content": "您的密码已到期！",
                        "content_html": "<p>您的密码已到期！</p>",
                    },
                ],
            },
        },
    }


@pytest.fixture()
def local_ds_plugin() -> DataSourcePlugin:
    return DataSourcePlugin.objects.get(id=DataSourcePluginEnum.LOCAL)


@pytest.fixture()
def bare_local_data_source(local_ds_plugin_cfg, local_ds_plugin) -> DataSource:
    """裸本地数据源（没有用户，部门等数据）"""
    return DataSource.objects.create(
        name=generate_random_string(),
        owner_tenant_id=DEFAULT_TENANT,
        plugin=local_ds_plugin,
        plugin_config=LocalDataSourcePluginConfig(**local_ds_plugin_cfg),
    )


@pytest.fixture()
def full_local_data_source(bare_local_data_source) -> DataSource:
    """携带用户，部门信息的本地数据源"""
    init_data_source_users_depts_and_relations(bare_local_data_source)
    return bare_local_data_source


@pytest.fixture()
def general_ds_plugin_cfg() -> Dict[str, Any]:
    return {
        "server_config": {
            "server_base_url": "http://bk.example.com:8090",
            "user_api_path": "/api/v1/users",
            "user_api_query_params": [{"key": "scope", "value": "company"}],
            "department_api_path": "/api/v1/departments",
            "department_api_query_params": [],
            "request_timeout": 5,
            "retries": 3,
        },
        "auth_config": {
            "method": "bearer_token",
            "bearer_token": "123456",
        },
    }


@pytest.fixture()
def general_ds_plugin() -> DataSourcePlugin:
    plugin, _ = DataSourcePlugin.objects.get_or_create(
        id=DataSourcePluginEnum.GENERAL,
        defaults={"name": "通用 HTTP 数据源"},
    )
    return plugin


@pytest.fixture()
def bare_general_data_source(general_ds_plugin_cfg, general_ds_plugin) -> DataSource:
    """裸通用 HTTP 数据源（没有用户，部门等数据）"""
    return DataSource.objects.create(
        name=generate_random_string(),
        owner_tenant_id=DEFAULT_TENANT,
        plugin=general_ds_plugin,
        plugin_config=GeneralDataSourcePluginConfig(**general_ds_plugin_cfg),
        sync_config={"sync_period": 60},
    )


@pytest.fixture()
def full_general_data_source(bare_general_data_source) -> DataSource:
    """携带用户，部门信息的通用 HTTP 数据源"""
    init_data_source_users_depts_and_relations(bare_general_data_source)
    return bare_general_data_source
