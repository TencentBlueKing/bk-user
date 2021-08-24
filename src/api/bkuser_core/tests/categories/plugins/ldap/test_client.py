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
import ldap3
import pytest
from bkuser_core.categories.plugins.ldap.client import LDAPClient
from bkuser_core.categories.plugins.ldap.exceptions import LdapCannotBeInitialized
from django.conf import settings
from ldap3.core.exceptions import LDAPInvalidDnError

pytestmark = pytest.mark.django_db


class TestClient:
    def test_error_server_load(self, test_ldap_config_provider):
        """测试无法正常连接 Ldap"""
        test_ldap_config_provider["connection_url"] = "ldap://localhost:3891"
        with pytest.raises(LdapCannotBeInitialized):
            LDAPClient(test_ldap_config_provider)

    def test_correct_server_load(self, test_ldap_config_provider):
        """测试正常连接 Ldap(仅当存在可用 Ldap 服务器时可用)"""
        LDAPClient(test_ldap_config_provider)

    def test_search(self, test_ldap_config_provider):
        """测试正常搜索(仅当存在可用 Ldap 服务器时可用)"""
        client = LDAPClient(test_ldap_config_provider)
        client.search(
            start_root=test_ldap_config_provider["basic_pull_node"],
            object_class=test_ldap_config_provider["user_class"],
        )

        with pytest.raises(LDAPInvalidDnError):
            client.search(start_root="xxx", object_class="xxx")

    def test_check(self, test_ldap_config_provider):
        """测试登陆"""
        client = LDAPClient(test_ldap_config_provider)

        with pytest.raises(ldap3.core.exceptions.LDAPBindError):
            client.check("admin", settings.TEST_LDAP["password"])

        # assets/ldap.ldif 中定义过
        client.check(settings.TEST_LDAP["user"], settings.TEST_LDAP["password"])
