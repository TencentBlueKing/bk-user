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
from unittest import mock

import pytest
from bkuser_core.categories.plugins.metas import ProfileMeta
from bkuser_core.departments.models import Department
from bkuser_core.tests.utils import make_simple_profile

pytestmark = pytest.mark.django_db


class TestSyncer:
    @pytest.mark.parametrize(
        "pre_created, users, expected_adding, expected_updating",
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

        with mock.patch.object(test_ldap_syncer.fetcher, "fetch") as fetch:
            fetch.return_value = [], [], users
            test_ldap_syncer._sync_profile()

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
        "departments, expected, expected_count",
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
                4,
            ),
            (
                [
                    {
                        "raw_dn": b"ou=shenzhen,ou=guangdong,dc=center,dc=com",
                        "dn": "ou=shenzhen,ou=guangdong,dc=center,dc=com",
                        "raw_attributes": {
                            "entryUUID": [b"shenzhen"],
                        },
                        "attributes": {
                            "entryUUID": "shenzhen",
                        },
                        "type": "searchResEntry",
                    },
                    {
                        "raw_dn": b"ou=guangdong,dc=center,dc=com",
                        "dn": "ou=guangdong,dc=center,dc=com",
                        "raw_attributes": {
                            "entryUUID": [b"guangdong"],
                        },
                        "attributes": {
                            "entryUUID": "guangdong",
                        },
                        "type": "searchResEntry",
                    },
                ],
                [["guangdong", "shenzhen"]],
                2,
            ),
            (
                [
                    {
                        "raw_dn": b"ou=guangdong,dc=center,dc=com",
                        "dn": "ou=guangdong,dc=center,dc=com",
                        "raw_attributes": {
                            "entryUUID": [b"guangdong"],
                        },
                        "attributes": {
                            "entryUUID": "guangdong",
                        },
                        "type": "searchResEntry",
                    },
                    {
                        "raw_dn": b"ou=shenzhen,ou=guangdong,dc=center,dc=com",
                        "dn": "ou=shenzhen,ou=guangdong,dc=center,dc=com",
                        "raw_attributes": {
                            "entryUUID": [b"shenzhen"],
                        },
                        "attributes": {
                            "entryUUID": "shenzhen",
                        },
                        "type": "searchResEntry",
                    },
                ],
                [["guangdong", "shenzhen"]],
                2,
            ),
        ],
    )
    def test_sync_departments(self, test_ldap_category, test_ldap_syncer, departments, expected, expected_count):
        """测试同步部门"""
        with mock.patch.object(test_ldap_syncer.fetcher, "fetch") as fetch:
            fetch.return_value = [], departments, []
            test_ldap_syncer._sync_department()

        for route in expected:
            parent = None
            for d in route:
                parent = Department.objects.get(name=d, parent=parent, category_id=test_ldap_syncer.category_id)

        assert Department.objects.filter(category_id=test_ldap_category.id).count() == expected_count

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
        with mock.patch.object(test_ldap_syncer.fetcher, "fetch") as fetch:
            fetch.return_value = groups, [], []
            test_ldap_syncer._sync_department()

        for route in expected:
            parent = None
            for d in route:
                parent = Department.objects.get(name=d, parent=parent, category_id=test_ldap_syncer.category_id)
