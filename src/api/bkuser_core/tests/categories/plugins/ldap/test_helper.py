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
from bkuser_core.categories.plugins.base import TypeList
from bkuser_core.categories.plugins.ldap.adaptor import department_adapter, user_adapter
from bkuser_core.categories.plugins.ldap.helper import DepartmentSyncHelper, ProfileSyncHelper
from bkuser_core.categories.plugins.ldap.metas import LdapDepartmentMeta, LdapProfileMeta
from bkuser_core.categories.plugins.ldap.models import LdapDepartment, LdapUserProfile
from bkuser_core.departments.models import Department, DepartmentThroughModel, Profile

pytestmark = pytest.mark.django_db


class TestDepartmentSyncHelper:
    @pytest.fixture(autouse=True)
    def setup(self, db_sync_manager):
        db_sync_manager.update_model_meta({"department": LdapDepartmentMeta, "profile": LdapProfileMeta})

    @pytest.mark.parametrize(
        "dept_info, expected_count",
        [(LdapDepartment(name="c", parent=LdapDepartment(name="b", parent=LdapDepartment(name="a"))), 3)],
    )
    def test_handle_department(
        self, test_ldap_category, test_ldap_config_provider, db_sync_manager, sync_context, dept_info, expected_count
    ):
        helper = DepartmentSyncHelper(
            test_ldap_category, db_sync_manager, TypeList[LdapDepartment](), sync_context, test_ldap_config_provider
        )
        helper._handle_department(dept_info)
        assert len(db_sync_manager[Department].adding_items) == expected_count

        dept = dept_info
        while dept:
            if dept.parent:
                assert (
                    db_sync_manager.magic_get(dept.key_field, target_meta=LdapDepartmentMeta).parent_id + 1
                    == db_sync_manager.magic_get(dept.key_field, target_meta=LdapDepartmentMeta).pk
                )
            dept = dept.parent

    @pytest.mark.parametrize(
        "departments, expected_logs, expected_count, expected_groups",
        [
            (
                [
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
                [
                    "handle department: guangdong/shenzhen<guangdong/shenzhen> (1/3)",
                    "handle department: beijing<beijing> (2/3)",
                    "handle department: Domain Controllers<Domain Controllers> (3/3)",
                ],
                4,
                [["guangdong", "shenzhen"], ["beijing"], ["Domain Controllers"]],
            )
        ],
    )
    def test_load_then_sync(
        self,
        test_ldap_category,
        db_sync_manager,
        sync_context,
        test_ldap_config_provider,
        caplog,
        departments,
        expected_logs,
        expected_count,
        expected_groups,
    ):
        target_objs = [
            department_adapter(code="", dept_meta=dept_meta, is_group=False, restrict_types=["ou", "cn"])
            for dept_meta in departments
        ]
        helper = DepartmentSyncHelper(
            test_ldap_category,
            db_sync_manager,
            TypeList[LdapDepartment].from_list(target_objs),
            sync_context,
            test_ldap_config_provider,
        )
        helper.load_to_memory()

        for log in expected_logs:
            assert log in caplog.text

        helper.db_sync_manager.sync_type(target_type=Department)
        assert Department.objects.filter(category_id=test_ldap_category.id).count() == expected_count

        for group in expected_groups:
            parent = None
            for member in group:
                parent = Department.objects.get(category_id=test_ldap_category.id, name=member, parent=parent)


class TestProfileSyncHelper:
    @pytest.mark.parametrize(
        "users, departments, expected_logs, expect_groups",
        [
            (
                [
                    {
                        "raw_dn": b"CN=Administrator,CN=Users,DC=center,DC=com",
                        "dn": "CN=Administrator,CN=Users,DC=center,DC=com",
                        "raw_attributes": {
                            "memberOf": [
                                b"CN=Group Policy Creator Owners,CN=Users,DC=center,DC=com",
                            ],
                            "sAMAccountName": [b"Administrator"],
                            "mail": [b"asdf@asdf.com"],
                            "displayName": [b"fakeman"],
                        },
                        "attributes": {"memberOf": ["CN=Group Policy Creator Owners,CN=Users,DC=center,DC=com"]},
                        "type": "searchResEntry",
                    },
                    {
                        "raw_dn": b"CN=Guest,CN=Users,DC=center,DC=com",
                        "dn": "CN=Guest,CN=Users,DC=center,DC=com",
                        "raw_attributes": {
                            "memberOf": [],
                            "sAMAccountName": [b"Guest"],
                            "mail": [b"asdf@asdf.com"],
                            "displayName": [b"fakeman"],
                        },
                        "attributes": {"memberOf": []},
                        "type": "searchResEntry",
                    },
                ],
                [["Users", "Administrator"], ["Users", "Group Policy Creator Owners"], ["Users", "Guest"]],
                ["handle profile: fakeman<Administrator> (1/2)", "handle profile: fakeman<Guest> (2/2)"],
                {"Guest": ['Users'], "Administrator": ['Users', 'Group Policy Creator Owners']},
            )
        ],
    )
    def test_load_then_sync(
        self,
        test_ldap_category,
        db_sync_manager,
        sync_context,
        profile_field_mapper,
        caplog,
        users,
        departments,
        expected_logs,
        expect_groups,
    ):
        for group in departments:
            parent = None
            for member in group:
                parent, _ = Department.objects.update_or_create(
                    name=member, parent=parent, defaults={"enabled": True}, category_id=test_ldap_category.pk
                )

        target_objs = [
            user_adapter(
                code=None, user_meta=user_meta, field_mapper=profile_field_mapper, restrict_types=["ou", "cn"]
            )
            for user_meta in users
        ]
        helper = ProfileSyncHelper(
            test_ldap_category,
            db_sync_manager,
            TypeList[LdapUserProfile].from_list(target_objs),
            sync_context,
        )
        helper.load_to_memory()

        for log in expected_logs:
            assert log in caplog.text

        helper.db_sync_manager.sync_type(target_type=Profile)
        helper.db_sync_manager.sync_type(target_type=DepartmentThroughModel)
        assert Profile.objects.filter(category_id=test_ldap_category.id).filter(
            username__in=expect_groups.keys()
        ).count() == len(expect_groups)
        for username, departments in expect_groups.items():
            assert sorted(
                DepartmentThroughModel.objects.filter(profile__username=username).values_list(
                    "department__name", flat=True
                )
            ) == sorted(departments)
