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
from bkuser_core.categories.plugins.metas import ProfileMeta
from bkuser_core.departments.models import Department
from bkuser_core.tests.utils import make_simple_profile

pytestmark = pytest.mark.django_db


class TestSyncer:
    @pytest.mark.parametrize(
        "dn,first,second",
        [
            ("cn=xxx,cn=qqq,ou=vvv,dc=test,dc=org", {"cn": "xxx"}, {"dc": "org"}),
            # 带空格
            ("cn=xx x,cn=qq q,ou=v vv,dc=test,dc=or g", {"cn": "xx x"}, {"dc": "or g"}),
        ],
    )
    def test_parse_tree(self, test_ldap_syncer, dn, first, second):
        """测试解析 dn 树"""
        b = test_ldap_syncer._parse_tree(dn)
        assert b[0] == first
        assert b[-1] == second

    @pytest.mark.parametrize(
        "dn,target,first,second",
        [
            (
                "cn=xxx,cn=qqq,ou=vvv,dc=test,dc=org",
                ["cn"],
                {"cn": "xxx"},
                {"cn": "qqq"},
            ),
            (
                "cn=xxx,ou=ddd,ou=vvv,dc=test,dc=org",
                ["ou"],
                {"ou": "ddd"},
                {"ou": "vvv"},
            ),
        ],
    )
    def test_parse_tree_restrict(self, test_ldap_syncer, dn, target, first, second):
        b = test_ldap_syncer._parse_tree(dn, target)

        assert b[0] == first
        assert b[1] == second

    @pytest.mark.parametrize(
        "dn,results",
        [
            (
                "cn=xx x,cn=qq q,ou=4+1,dc=test,dc=or g",
                [
                    {"cn": "xx x"},
                    {"cn": "qq q"},
                    {"ou": "4\\+1"},
                    {"dc": "test"},
                    {"dc": "or g"},
                ],
            ),
            (
                "cn=xx x,cn=《梦工厂大冒险》攻坚组,ou=4+1,dc=test,dc=or g",
                [
                    {"cn": "xx x"},
                    {"cn": "《梦工厂大冒险》攻坚组"},
                    {"ou": "4\\+1"},
                    {"dc": "test"},
                    {"dc": "or g"},
                ],
            ),
        ],
    )
    def test_parse_tree_with_special(self, test_ldap_syncer, dn, results):
        """测试解析 dn 树，特殊字符"""
        assert test_ldap_syncer._parse_tree(dn) == results

    @pytest.mark.parametrize(
        "pre_created,users,expected_adding, expected_updating",
        [
            (
                [],
                [
                    {
                        "uri": ["ldap://center.com/CN=Configuration,DC=center,DC=com"],
                        "type": "searchResRef",
                    },
                    # AD, different source of username
                    {
                        "raw_dn": b"CN=dddd aaaaa,OU=shenzhen,DC=center,DC=com",
                        "dn": "CN=dddd aaaaa,OU=shenzhen,DC=center,DC=com",
                        "raw_attributes": {
                            "displayName": [b"dddd aaaaa"],
                            "sAMAccountName": [b"wwowowo"],
                            "mail": [b"aaaa@asdf.com"],
                            "mobile": [b"123412341234"],
                            "memberOf": [],
                        },
                        "attributes": {
                            "displayName": "dddd aaaaa",
                            "sAMAccountName": "qfqfqf",
                            "mail": "aaaa@asdf.com",
                            "mobile": "123412341234",
                            "memberOf": [],
                        },
                        "type": "searchResEntry",
                    },
                    {
                        "raw_dn": b"CN=dddd aaaaa,OU=shenzhen,DC=center,DC=com",
                        "dn": "CN=dddd aaaaa,OU=shenzhen,DC=center,DC=com",
                        "raw_attributes": {
                            "displayName": [b"dddd aaaaa"],
                            "cn": [b"qfqfqf"],
                            "mail": [b"aaaa@asdf.com"],
                            "telephonenumber": [b"123412341234"],
                            "memberOf": [],
                        },
                        "attributes": {
                            "displayName": "dddd aaaaa",
                            "sAMAccountName": "qfqfqf",
                            "mail": "aaaa@asdf.com",
                            "mobile": "123412341234",
                            "memberOf": [],
                        },
                        "type": "searchResEntry",
                    },
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
                            "cn": [b"Administrator"],
                            "mail": [b"asdf@asdf.com"],
                            "telephonenumber": [b"11122334"],
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
                            "mobile": "11122334",
                            "displayName": [],
                        },
                        "type": "searchResEntry",
                    },
                ],
                ["qfqfqf", "Administrator"],
                [],
            ),
            (
                ["qfqfqf"],
                [
                    {
                        "raw_dn": b"CN=dddd aaaaa,OU=shenzhen,DC=center,DC=com",
                        "dn": "CN=dddd aaaaa,OU=shenzhen,DC=center,DC=com",
                        "raw_attributes": {
                            "displayName": [b"dddd aaaaa"],
                            "cn": [b"qfqfqf"],
                            "mail": [b"aaaa@asdf.com"],
                            "telephonenumber": [b"123412341234"],
                            "memberOf": [],
                        },
                        "attributes": {
                            "displayName": "dddd aaaaa",
                            "sAMAccountName": "qfqfqf",
                            "mail": "aaaa@asdf.com",
                            "mobile": "123412341234",
                            "memberOf": [],
                        },
                        "type": "searchResEntry",
                    },
                    {
                        "raw_dn": b"CN=Administrator,CN=Users,DC=center,DC=com",
                        "dn": "CN=Administrator,CN=Users,DC=center,DC=com",
                        "raw_attributes": {
                            "memberOf": [],
                            "cn": [b"Administrator"],
                            "mail": [b"asdf@asdf.com"],
                            "telephonenumber": [b"11122334"],
                            "displayName": [],
                        },
                        "attributes": {
                            "memberOf": [],
                            "sAMAccountName": "Administrator",
                            "mail": "asdf@asdf.com",
                            "mobile": "11122334",
                            "displayName": [],
                        },
                        "type": "searchResEntry",
                    },
                ],
                ["Administrator"],
                ["qfqfqf"],
            ),
        ],
    )
    def test_sync_users(self, pre_created, test_ldap_syncer, users, expected_adding, expected_updating):
        """测试同步用户"""
        for p in pre_created:
            make_simple_profile(p, force_create_params={"category_id": test_ldap_syncer.category_id})

        test_ldap_syncer._sync_users(users)

        for k in expected_adding:
            assert (
                test_ldap_syncer.db_sync_manager.magic_get(k, ProfileMeta)
                in test_ldap_syncer.db_sync_manager._sets[ProfileMeta.target_model].adding_items
            )

        for k in expected_updating:
            assert (
                test_ldap_syncer.db_sync_manager.magic_get(k, ProfileMeta)
                in test_ldap_syncer.db_sync_manager._sets[ProfileMeta.target_model].updating_items
            )

    @pytest.mark.parametrize(
        "departments,expected",
        [
            (
                [
                    {
                        "uri": ["ldap://center.com/CN=Configuration,DC=center,DC=com"],
                        "type": "searchResRef",
                    },
                    {
                        "uri": ["ldap://DomainDnsZones.center.com/DC=DomainDnsZones,DC=center,DC=com"],
                        "type": "searchResRef",
                    },
                    {
                        "uri": ["ldap://ForestDnsZones.center.com/DC=ForestDnsZones,DC=center,DC=com"],
                        "type": "searchResRef",
                    },
                    {
                        "raw_dn": b"ou=shenzhen,ou=guangdong,dc=center,dc=com",
                        "dn": "ou=shenzhen,ou=guangdong,dc=center,dc=com",
                        "raw_attributes": {},
                        "attributes": {},
                        "type": "searchResEntry",
                    },
                    {
                        "raw_dn": b"ou=beijing,dc=center,dc=com",
                        "dn": "ou=beijing,dc=center,dc=com",
                        "raw_attributes": {},
                        "attributes": {},
                        "type": "searchResEntry",
                    },
                    {
                        "raw_dn": b"ou=Domain Controllers,dc=center,dc=com",
                        "dn": "ou=Domain Controllers,dc=center,dc=com",
                        "raw_attributes": {},
                        "attributes": {},
                        "type": "searchResEntry",
                    },
                ],
                [["guangdong", "shenzhen"], ["beijing"]],
            )
        ],
    )
    def test_sync_departments(self, test_ldap_syncer, departments, expected):
        """测试同步部门"""
        test_ldap_syncer._sync_departments(departments)

        for route in expected:
            parent = None
            for d in route:
                parent = Department.objects.get(name=d, parent=parent, category_id=test_ldap_syncer.category_id)

    @pytest.mark.parametrize(
        "groups,expected",
        [
            (
                [
                    {
                        "raw_dn": b"cn=ffff,ou=asdf,dc=example,dc=org",
                        "dn": "cn=ffff,ou=asdf,dc=example,dc=org",
                        "raw_attributes": {
                            "entryUUID": [b"4e4d8a12-b753-103a-8d1a-438164e36e34"],
                        },
                        "attributes": {
                            "entryUUID": "4e4d8a12-b753-103a-8d1a-438164e36e34",
                        },
                        "type": "searchResEntry",
                    },
                    {
                        "raw_dn": b"cn=qqqq,cn=dddd,dc=example,dc=org",
                        "dn": "cn=qqqq,cn=dddd,dc=example,dc=org",
                        "raw_attributes": {
                            "entryUUID": [b"qwera12-b753-103a-8d1a-438164e36e34"],
                        },
                        "attributes": {
                            "entryUUID": "qwera12-b753-103a-8d1a-438164e36e34",
                        },
                        "type": "searchResEntry",
                    },
                ],
                [["asdf", "ffff"], ["dddd", "qqqq"]],
            ),
            (
                [
                    {
                        "raw_dn": b"cn=wwww,dc=example,dc=org",
                        "dn": "cn=wwww,dc=example,dc=org",
                        "raw_attributes": {
                            "entryUUID": [b"4e4d8a12-b753-103a-8d1a-438164e36e34"],
                        },
                        "attributes": {
                            "entryUUID": "4e4d8a12-b753-103a-8d1a-438164e36e34",
                        },
                        "type": "searchResEntry",
                    },
                ],
                [["wwww"]],
            ),
        ],
    )
    def test_sync_groups(self, test_ldap_syncer, groups, expected):
        """测试同步组织"""
        test_ldap_syncer._sync_departments(groups, True)

        for route in expected:
            parent = None
            for d in route:
                parent = Department.objects.get(name=d, parent=parent, category_id=test_ldap_syncer.category_id)


class TestFetcher:
    """Test Fetcher"""
