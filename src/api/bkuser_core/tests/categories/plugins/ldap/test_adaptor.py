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
from bkuser_core.categories.plugins.ldap.adaptor import (
    RDN,
    department_adapter,
    parse_dn_tree,
    parse_dn_value_list,
    user_adapter,
)
from bkuser_core.categories.plugins.ldap.models import LdapDepartment, LdapUserProfile


@pytest.mark.parametrize(
    "dn, restrict_types, expected",
    [
        (
            "CN=Jeff Smith,OU=Sales,DC=Fabrikam,DC=COM",
            [],
            ["Jeff Smith", "Sales", "Fabrikam", "COM"],
        ),
        (
            "CN=Jeff Smith,OU=Sales,DC=Fabrikam,DC=COM",
            None,
            ["Jeff Smith", "Sales", "Fabrikam", "COM"],
        ),
        ("CN=Jeff Smith,OU=Sales,DC=Fabrikam,DC=COM", ["DC"], ["Fabrikam", "COM"]),
        (
            "CN=Karen Berge,CN=admin,DC=corp,DC=Fabrikam,DC=COM",
            ["CN"],
            ["Karen Berge", "admin"],
        ),
        (
            "CN=Karen Berge,CN=admin,DC=corp,DC=Fabrikam,DC=COM",
            ["CN", "DC"],
            ["Karen Berge", "admin", "corp", "Fabrikam", "COM"],
        ),
        (
            "CN=Karen Berge,CN=admin,DC=corp,DC=Fabrikam,DC=COM",
            [],
            ["Karen Berge", "admin", "corp", "Fabrikam", "COM"],
        ),
    ],
)
def test_parse_dn_value_list(dn, restrict_types, expected):
    assert parse_dn_value_list(dn, restrict_types) == expected


@pytest.mark.parametrize(
    "dn, restrict_types, expected",
    [
        (
            "CN=Jeff Smith,OU=Sales,DC=Fabrikam,DC=COM",
            [],
            [
                RDN(type="CN", value="Jeff Smith", separator=","),
                RDN(type="OU", value="Sales", separator=","),
                RDN(type="DC", value="Fabrikam", separator=","),
                RDN(type="DC", value="COM", separator=""),
            ],
        ),
        (
            "CN=Jeff Smith,OU=Sales,DC=Fabrikam,DC=COM",
            None,
            [
                RDN(type="CN", value="Jeff Smith", separator=","),
                RDN(type="OU", value="Sales", separator=","),
                RDN(type="DC", value="Fabrikam", separator=","),
                RDN(type="DC", value="COM", separator=""),
            ],
        ),
        (
            "CN=Jeff Smith,OU=Sales,DC=Fabrikam,DC=COM",
            ["DC"],
            [
                RDN(type="DC", value="Fabrikam", separator=","),
                RDN(type="DC", value="COM", separator=""),
            ],
        ),
        (
            "CN=Karen Berge,CN=admin,DC=corp,DC=Fabrikam,DC=COM",
            [],
            [
                RDN(type="CN", value="Karen Berge", separator=","),
                RDN(type="CN", value="admin", separator=","),
                RDN(type="DC", value="corp", separator=","),
                RDN(type="DC", value="Fabrikam", separator=","),
                RDN(type="DC", value="COM", separator=""),
            ],
        ),
        (
            "CN=Karen Berge,CN=admin,DC=corp,DC=Fabrikam,DC=COM",
            ["CN"],
            [
                RDN(type="CN", value="Karen Berge", separator=","),
                RDN(type="CN", value="admin", separator=","),
            ],
        ),
        (
            "CN=Karen Berge,CN=admin,DC=corp,DC=Fabrikam,DC=COM",
            ["CN", "DC"],
            [
                RDN(type="CN", value="Karen Berge", separator=","),
                RDN(type="CN", value="admin", separator=","),
                RDN(type="DC", value="corp", separator=","),
                RDN(type="DC", value="Fabrikam", separator=","),
                RDN(type="DC", value="COM", separator=""),
            ],
        ),
        (
            "cn=xx x,cn=《梦工厂大冒险》攻坚组,ou=4+1,dc=test,dc=or g",
            [],
            [
                RDN(type="cn", value="xx x", separator=","),
                RDN(type="cn", value="《梦工厂大冒险》攻坚组", separator=","),
                RDN(type="ou", value="4\\+1", separator=","),
                RDN(type="dc", value="test", separator=","),
                RDN(type="dc", value="or g", separator=""),
            ],
        ),
        (
            "cn=xx x,cn=qq q,ou=4+1,dc=test,dc=or g",
            [],
            [
                RDN(type="cn", value="xx x", separator=","),
                RDN(type="cn", value="qq q", separator=","),
                RDN(type="ou", value="4\\+1", separator=","),
                RDN(type="dc", value="test", separator=","),
                RDN(type="dc", value="or g", separator=""),
            ],
        ),
    ],
)
def test_parse_dn_tree(dn, restrict_types, expected):
    assert parse_dn_tree(dn, restrict_types) == expected


@pytest.mark.parametrize(
    "user_meta, restrict_types, expected",
    [
        (
            {
                "raw_dn": b"CN=Administrator,CN=Users,DC=center,DC=com",
                "dn": "CN=Administrator,CN=Users,DC=center,DC=com",
                "raw_attributes": {
                    "memberOf": [
                        b"CN=Group Policy Creator Owners,CN=Users,DC=center,DC=com",
                        b"CN=Domain Admins,CN=Users,DC=center,DC=com",
                        b"CN=Enterprise Admins,CN=Users,DC=center,DC=com",
                        b"CN=Schema Admins,CN=Users,DC=center,DC=com",
                        b"CN=Administrators,CN=Builtin,DC=center,DC=com",
                    ],
                    "sAMAccountName": [b"Administrator"],
                    "mail": [b"asdf@asdf.com"],
                    "displayName": [],
                },
                "attributes": {
                    "memberOf": [
                        "CN=Group Policy Creator Owners,CN=Users,DC=center,DC=com",
                        "CN=Domain Admins,CN=Users,DC=center,DC=com",
                        "CN=Enterprise Admins,CN=Users,DC=center,DC=com",
                        "CN=Schema Admins,CN=Users,DC=center,DC=com",
                        "CN=Administrators,CN=Builtin,DC=center,DC=com",
                    ],
                    "sAMAccountName": "Administrator",
                    "mail": "asdf@asdf.com",
                    "displayName": [],
                },
                "type": "searchResEntry",
            },
            [],
            LdapUserProfile(
                username="Administrator",
                email="asdf@asdf.com",
                telephone="",
                display_name="",
                code="dummy",
                departments=[
                    ["com", "center", "Users"],
                    ["com", "center", "Users", "Group Policy Creator Owners"],
                    ["com", "center", "Users", "Domain Admins"],
                    ["com", "center", "Users", "Enterprise Admins"],
                    ["com", "center", "Users", "Schema Admins"],
                    ["com", "center", "Builtin", "Administrators"],
                ],
            ),
        ),
        (
            {
                "raw_dn": b"CN=Guest,CN=Users,DC=center,DC=com",
                "dn": "CN=Guest,CN=Users,DC=center,DC=com",
                "raw_attributes": {
                    "memberOf": [b"CN=Guests,OU=Builtin,DC=center,DC=com"],
                    "sAMAccountName": [b"Guest"],
                    "displayName": [],
                    "mail": [],
                },
                "attributes": {
                    "memberOf": ["CN=Guests,CN=Builtin,DC=center,DC=com"],
                    "sAMAccountName": "Guest",
                    "displayName": [],
                    "mail": [],
                },
                "type": "searchResEntry",
            },
            ["OU", "CN"],
            LdapUserProfile(
                username="Guest",
                email="",
                telephone="",
                display_name="",
                code="dummy",
                departments=[
                    ["Users"],
                    ["Builtin", "Guests"],
                ],
            ),
        ),
    ],
)
def test_user_adaptor(profile_field_mapper, user_meta, restrict_types, expected):
    assert (
        user_adapter(
            code="dummy",
            user_meta=user_meta,
            field_mapper=profile_field_mapper,
            restrict_types=restrict_types,
        )
        == expected
    )


@pytest.mark.parametrize(
    "dept_meta, restrict_types, expected",
    [
        (
            {
                "raw_dn": b"OU=shenzhen,OU=guangdong,DC=center,DC=com",
                "dn": "OU=shenzhen,OU=guangdong,DC=center,DC=com",
                "raw_attributes": {},
                "attributes": {},
                "type": "searchResEntry",
            },
            ["OU", "CN"],
            LdapDepartment(
                name="shenzhen",
                parent=LdapDepartment(name="guangdong"),
                code="dummy",
            ),
        ),
        (
            {
                "raw_dn": b"OU=shenzhen,OU=guangdong,OU=china,DC=center,DC=com",
                "dn": "OU=shenzhen,OU=guangdong,OU=china,DC=center,DC=com",
                "raw_attributes": {},
                "attributes": {},
                "type": "searchResEntry",
            },
            ["OU", "CN"],
            LdapDepartment(
                name="shenzhen",
                parent=LdapDepartment(name="guangdong", parent=LdapDepartment(name="china")),
                code="dummy",
            ),
        ),
    ],
)
def test_department_adaptor(dept_meta, restrict_types, expected):
    assert (
        department_adapter(
            code="dummy",
            dept_meta=dept_meta,
            is_group=False,
            restrict_types=restrict_types,
        )
        == expected
    )
