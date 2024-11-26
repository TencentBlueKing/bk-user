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
from bkuser.plugins.ldap.plugin import LDAPDataSourcePlugin
from bkuser.plugins.models import RawDataSourceDepartment, RawDataSourceUser


class TestLDAPDataSourcePlugin:
    @pytest.mark.usefixtures("_mock_ldap_client")
    def test_get_departments(self, ldap_ds_cfg, logger):
        plugin = LDAPDataSourcePlugin(ldap_ds_cfg, logger)
        departments = plugin.fetch_departments()
        assert len(departments) == 12  # noqa: PLR2004

        assert departments[0] == RawDataSourceDepartment(
            code="97aaa370-0e9d-103f-8e7f-fb1e46baa127",
            name="group_baa",
            parent="97a9aa88-0e9d-103f-8e7e-fb1e46baa127",
            extras={
                "attr_type": "ou",
                "dn": "ou=group_baa,ou=center_ba,ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
                "parent_dn": "ou=center_ba,ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
            },
        )

        assert departments[-1] == RawDataSourceDepartment(
            code="97b2869e-0e9d-103f-8e83-fb1e46baa127",
            name="center_aa",
            parent="97a63966-0e9d-103f-8e78-fb1e46baa127",
            extras={
                "attr_type": "cn",
                "dn": "cn=center_aa,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
                "parent_dn": "ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
            },
        )

    @pytest.mark.usefixtures("_mock_ldap_client")
    def test_get_departments_without_group(self, ldap_ds_cfg, logger):
        ldap_ds_cfg.user_group_config.enabled = False
        plugin = LDAPDataSourcePlugin(ldap_ds_cfg, logger)
        departments = plugin.fetch_departments()
        assert len(departments) == 9  # noqa: PLR2004

    @pytest.mark.usefixtures("_mock_ldap_client")
    def test_get_users(self, ldap_ds_cfg, logger):
        plugin = LDAPDataSourcePlugin(ldap_ds_cfg, logger)
        plugin.fetch_departments()
        users = plugin.fetch_users()
        assert len(users) == 10  # noqa: PLR2004

        assert users[0] == RawDataSourceUser(
            code="97b9bdce-0e9d-103f-8e8c-fb1e46baa127",
            properties={
                "dn": "cn=baishier,ou=group_baa,ou=center_ba,ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
                "givenName": "shier",
                "sn": "bai",
                "cn": "baishier",
                "uid": "baishier",
                "manager": "cn=lushi,ou=group_aba,ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
            },
            leaders=["97b65b84-0e9d-103f-8e88-fb1e46baa127"],
            departments=["97aaa370-0e9d-103f-8e7f-fb1e46baa127"],
        )

        assert users[2] == RawDataSourceUser(
            code="97b65b84-0e9d-103f-8e88-fb1e46baa127",
            properties={
                "dn": "cn=lushi,ou=group_aba,ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
                "givenName": "shi",
                "sn": "lu",
                "cn": "lushi",
                "uid": "lushi",
                "manager": "cn=maiba,ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com"
                + " cn=wangwu,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
            },
            leaders=["97b534de-0e9d-103f-8e86-fb1e46baa127", "97b33a9e-0e9d-103f-8e84-fb1e46baa127"],
            departments=["97a93076-0e9d-103f-8e7d-fb1e46baa127", "97b93908-0e9d-103f-8e8b-fb1e46baa127"],
        )


class TestLDAPDataSourcePluginMultipleBaseDNs:
    @pytest.mark.usefixtures("_mock_ldap_client")
    def test_get_departments(self, ldap_ds_cfg, logger):
        base_dns = [
            "ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
            "ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
        ]
        ldap_ds_cfg.data_config.dept_search_base_dns = base_dns
        ldap_ds_cfg.user_group_config.search_base_dns = base_dns
        plugin = LDAPDataSourcePlugin(ldap_ds_cfg, logger)
        departments = plugin.fetch_departments()
        # 注意：cn=dept_b,ou=company,dc=bk,dc=example,dc=com 不匹配
        assert len(departments) == 6  # noqa: PLR2004

    @pytest.mark.usefixtures("_mock_ldap_client")
    def test_get_departments_without_group(self, ldap_ds_cfg, logger):
        ldap_ds_cfg.data_config.dept_search_base_dns = [
            "ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
            "ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
        ]
        ldap_ds_cfg.user_group_config.enabled = False
        plugin = LDAPDataSourcePlugin(ldap_ds_cfg, logger)
        departments = plugin.fetch_departments()
        assert len(departments) == 5  # noqa: PLR2004

    @pytest.mark.usefixtures("_mock_ldap_client")
    def test_get_users(self, ldap_ds_cfg, logger):
        ldap_ds_cfg.data_config.user_search_base_dns = [
            "ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
            "ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
        ]
        plugin = LDAPDataSourcePlugin(ldap_ds_cfg, logger)
        plugin.fetch_departments()
        users = plugin.fetch_users()
        assert len(users) == 5  # noqa: PLR2004
