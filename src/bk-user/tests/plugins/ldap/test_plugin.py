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

import uuid

import pytest
from bkuser.plugins.ldap.plugin import LDAPDataSourcePlugin
from bkuser.plugins.models import RawDataSourceDepartment, RawDataSourceUser


@pytest.fixture(
    params=[("_mock_ldap_client", "entryUUID"), ("_mock_ad_ldap_client", "objectGUID")], ids=["openldap", "ad"]
)
def ldap_directory_case(request):
    mock_fixture, id_attribute = request.param
    request.getfixturevalue(mock_fixture)
    return id_attribute


def _set_id_attribute(ldap_ds_cfg, id_attribute: str):
    ldap_ds_cfg.data_config.id_attribute = id_attribute


def _assert_first_department(department):
    assert department == RawDataSourceDepartment(
        code="97aaa370-0e9d-103f-8e7f-fb1e46baa127",
        name="group_baa",
        parent="97a9aa88-0e9d-103f-8e7e-fb1e46baa127",
        extras={
            "attr_type": "ou",
            "dn": "ou=group_baa,ou=center_ba,ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
            "parent_dn": "ou=center_ba,ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
        },
    )


def _assert_last_department(department):
    assert department == RawDataSourceDepartment(
        code="97b2869e-0e9d-103f-8e83-fb1e46baa127",
        name="center_aa",
        parent="97a63966-0e9d-103f-8e78-fb1e46baa127",
        extras={
            "attr_type": "cn",
            "dn": "cn=center_aa,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
            "parent_dn": "ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        },
    )


def _assert_first_user(user):
    assert user == RawDataSourceUser(
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


def _assert_lushi_user(user):
    assert user == RawDataSourceUser(
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


def _assert_test_connection_department_sample(department):
    assert department == RawDataSourceDepartment(
        code="97aaa370-0e9d-103f-8e7f-fb1e46baa127",
        name="group_baa",
        parent="ou=center_ba,ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
        extras={
            "attr_type": "ou",
            "dn": "ou=group_baa,ou=center_ba,ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
        },
    )


def _assert_test_connection_user_sample(user):
    assert user == RawDataSourceUser(
        code="97b9bdce-0e9d-103f-8e8c-fb1e46baa127",
        properties={
            "dn": "cn=baishier,ou=group_baa,ou=center_ba,ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
            "givenName": "shier",
            "sn": "bai",
            "cn": "baishier",
            "uid": "baishier",
            "manager": "cn=lushi,ou=group_aba,ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
        },
        leaders=[],
        departments=[],
    )


class TestLDAPDataSourcePlugin:
    def test_get_departments(self, ldap_ds_cfg, logger, ldap_directory_case):
        _set_id_attribute(ldap_ds_cfg, ldap_directory_case)
        plugin = LDAPDataSourcePlugin(ldap_ds_cfg, logger)
        departments = plugin.fetch_departments()
        assert len(departments) == 12  # noqa: PLR2004

        _assert_first_department(departments[0])
        _assert_last_department(departments[-1])

    def test_get_departments_without_group(self, ldap_ds_cfg, logger, ldap_directory_case):
        _set_id_attribute(ldap_ds_cfg, ldap_directory_case)
        ldap_ds_cfg.user_group_config.enabled = False
        plugin = LDAPDataSourcePlugin(ldap_ds_cfg, logger)
        departments = plugin.fetch_departments()
        assert len(departments) == 9  # noqa: PLR2004

    def test_get_users(self, ldap_ds_cfg, logger, ldap_directory_case):
        _set_id_attribute(ldap_ds_cfg, ldap_directory_case)
        plugin = LDAPDataSourcePlugin(ldap_ds_cfg, logger)
        plugin.fetch_departments()
        users = plugin.fetch_users()
        assert len(users) == 10  # noqa: PLR2004

        _assert_first_user(users[0])
        _assert_lushi_user(users[2])

    def test_test_connection(self, ldap_ds_cfg, logger, ldap_directory_case):
        _set_id_attribute(ldap_ds_cfg, ldap_directory_case)
        plugin = LDAPDataSourcePlugin(ldap_ds_cfg, logger)

        result = plugin.test_connection()

        assert result.error_message == ""
        assert result.extras is not None
        department_data = result.extras["department_data"]
        user_data = result.extras["user_data"]
        assert isinstance(department_data, dict)
        assert isinstance(user_data, dict)
        _assert_test_connection_department_sample(result.department)
        _assert_test_connection_user_sample(result.user)

        # OpenLDAP 场景 entryUUID 是文本，原样保留；AD 场景 objectGUID 是无法以 UTF-8 表示的
        # 二进制数据，会在清洗阶段转成空字符串。两种情况对 extras 调用方而言都是 str
        assert isinstance(department_data[ldap_directory_case], str)
        assert isinstance(user_data[ldap_directory_case], str)


class TestLDAPDataSourcePluginMultipleBaseDNs:
    @pytest.mark.usefixtures("_mock_ldap_client")
    def test_get_departments(self, ldap_ds_cfg, logger):
        search_base_dns = [
            "ou=center_ab,ou=dept_a,ou=company,dc=bk,dc=example,dc=com",
            "ou=dept_b,ou=company,dc=bk,dc=example,dc=com",
        ]
        ldap_ds_cfg.data_config.dept_search_base_dns = search_base_dns
        ldap_ds_cfg.user_group_config.search_base_dns = search_base_dns
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


class TestGetUUIDValue:
    """测试 _get_uuid_value 方法"""

    def test_string_value(self):
        """OpenLDAP entryUUID 返回的是字符串，直接使用"""
        uuid_str = "97aaa370-0e9d-103f-8e7f-fb1e46baa127"
        result = LDAPDataSourcePlugin._get_uuid_value(uuid_str)
        assert result == uuid_str

    def test_bytes_value(self):
        """AD objectGUID 返回的是二进制数据（bytes_le 格式），需转换为 UUID 字符串"""
        uuid_str = "97aaa370-0e9d-103f-8e7f-fb1e46baa127"
        binary_value = uuid.UUID(uuid_str).bytes_le
        result = LDAPDataSourcePlugin._get_uuid_value(binary_value)
        assert result == uuid_str

    def test_invalid_bytes_value(self):
        with pytest.raises(ValueError, match="invalid LDAP UUID bytes value"):
            LDAPDataSourcePlugin._get_uuid_value(b"invalid-guid")


class TestSafeStrValue:
    """测试 _safe_str_value 方法对 LDAP 属性值的转换"""

    def test_plain_str_value(self):
        assert LDAPDataSourcePlugin._safe_str_value("zhangsan") == "zhangsan"

    def test_utf8_bytes_value(self):
        """LDAP 有些 server 会把字符串用 bytes 返回，应能直接 UTF-8 解码回字符串"""
        assert LDAPDataSourcePlugin._safe_str_value("张三".encode("utf-8")) == "张三"

    def test_non_utf8_bytes_value_returns_empty(self):
        """真二进制（如 jpegPhoto）无法 UTF-8 解码，返回空字符串"""
        raw = b"\x89PNG\r\n\x1a\n\x00\x00\xff\xfe"
        assert LDAPDataSourcePlugin._safe_str_value(raw) == ""

    def test_non_str_non_bytes_value(self):
        """其他类型走 str() 转换"""
        assert LDAPDataSourcePlugin._safe_str_value(123) == "123"
        assert LDAPDataSourcePlugin._safe_str_value(None) == "None"
