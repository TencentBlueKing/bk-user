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

from bkuser_core.categories.plugins.base import DBSyncManager, SyncContext
from bkuser_core.categories.plugins.ldap.adaptor import ProfileFieldMapper


@pytest.fixture()
def ldap_config():
    return {
        "user_member_of": "memberOf",
        "basic_pull_node": "DC=center,DC=com",
        "user_group_description": "description",
        "user_group_name": "cn",
        "user_group_class": "groupOfUniqueNames",
        "mad_fields": [],
        "bk_fields": "",
        "telephone": "",
        "email": "mail",
        "display_name": "displayName",
        "username": "sAMAccountName",
        "organization_class": "organizationalUnit",
        "user_class": "user",
        "user_group_filter": "(objectclass=groupOfUniqueNames)",
        "user_filter": "(&(objectCategory=Person)(sAMAccountName=*))",
        "password": "password of Administrator",
        "user": "CN=Administrator,CN=admin,DC=corp,DC=Fabrikam,DC=COM",
        "base_dn": "DC=center,DC=com",
        "pull_cycle": 60,
        "timeout_setting": 120,
        "connection_url": "ldap://127.0.0.1:389",
        "ssl_encryption": "无",
    }


@pytest.fixture()
def profile_field_mapper(ldap_config):
    return ProfileFieldMapper(config_loader=ldap_config)


@pytest.fixture
def sync_context():
    return SyncContext()


@pytest.fixture
def db_sync_manager():
    return DBSyncManager()
