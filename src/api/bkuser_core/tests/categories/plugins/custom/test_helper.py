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

from bkuser_core.categories.plugins.custom.helpers import DepSyncHelper, ProSyncHelper
from bkuser_core.categories.plugins.custom.metas import CustomDepartmentMeta, CustomProfileMeta
from bkuser_core.categories.plugins.custom.models import CustomDepartment, CustomProfile, CustomTypeList
from bkuser_core.departments.models import Department, DepartmentThroughModel
from bkuser_core.profiles.models import LeaderThroughModel, Profile

pytestmark = pytest.mark.django_db


@pytest.fixture
def make_pro_sync_helper(test_custom_category, db_sync_manager, sync_context):
    def helper(target_obj_list: CustomTypeList) -> ProSyncHelper:
        db_sync_manager.update_model_meta({"department": CustomDepartmentMeta, "profile": CustomProfileMeta})
        return ProSyncHelper(test_custom_category, db_sync_manager, target_obj_list, context=sync_context)

    return helper


@pytest.fixture
def make_dep_sync_helper(test_custom_category, db_sync_manager, sync_context):
    def helper(target_obj_list: CustomTypeList) -> DepSyncHelper:
        db_sync_manager.update_model_meta({"department": CustomDepartmentMeta, "profile": CustomProfileMeta})
        return DepSyncHelper(test_custom_category, db_sync_manager, target_obj_list, context=sync_context)

    return helper


class TestDepHelper:
    @pytest.mark.parametrize(
        "dict_objs, expected",
        [
            (
                [{"name": "测试部门", "code": "dep1", "parent": None}],
                [["测试部门"]],
            ),
            (
                [
                    {"name": "测试部门", "code": "dep1", "parent": None},
                    {"name": "测试部门2", "code": "dep2", "parent": "dep1"},
                ],
                [["测试部门", "测试部门2"]],
            ),
            (
                [
                    {"name": "测试部门", "code": "dep1", "parent": None},
                    {"name": "测试部门2", "code": "dep2", "parent": "dep1"},
                    {"name": "测试部门3", "code": "dep3", "parent": "dep2"},
                    {"name": "测试部门4", "code": "dep4", "parent": None},
                ],
                [["测试部门", "测试部门2", "测试部门3"], ["测试部门4"]],
            ),
        ],
    )
    def test_sync(self, make_dep_sync_helper, dict_objs, expected):
        helper = make_dep_sync_helper(CustomTypeList.from_list([CustomDepartment.from_dict(x) for x in dict_objs]))
        helper.load_to_memory()

        helper.db_sync_manager.sync_type(target_type=Department)
        for group in expected:
            parent = None
            for d in group:
                parent = Department.objects.get(category_id=helper.category.id, name=d, parent=parent)


class TestProfileHelper:
    @pytest.mark.parametrize(
        "dict_objs,department_objs",
        [
            (
                [
                    {
                        "username": "fake-user",
                        "email": "fake@test.com",
                        "code": "code-1",
                        "display_name": "fakeman",
                        "telephone": "13111123445",
                        "leaders": [],
                        "departments": [],
                        "extras": {"aaa": "xxxx", "bbb": "qqqq", "uniquetest": "vvvv"},
                        "position": 0,
                    },
                    {
                        "username": "fake-user-2",
                        "email": "fake2@test.com",
                        "code": "code-2",
                        "display_name": "fakeman2",
                        "telephone": "13111123445",
                        "leaders": ["code-1"],
                        "departments": ["dep1"],
                        "extras": {"aaa": "xxxx", "bbb": "qqqq", "uniquetest": "vvvv"},
                        "position": 0,
                    },
                ],
                [{"name": "测试部门", "code": "dep1", "parent": None}],
            ),
            (
                [
                    {
                        "username": "fake-user-2",
                        "email": "fake2@test.com",
                        "code": "code-2",
                        "display_name": "fakeman2",
                        "telephone": "13111123445",
                        "leaders": ["code-1"],
                        "departments": ["dep1", "dep2"],
                        "extras": {"aaa": "xxxx", "bbb": "qqqq", "uniquetest": "vvvv"},
                        "position": 0,
                    },
                ],
                [
                    {"name": "测试部门", "code": "dep1", "parent": None},
                    {"name": "测试部门2", "code": "dep2", "parent": None},
                ],
            ),
        ],
    )
    def test_sync(self, make_pro_sync_helper, make_dep_sync_helper, dict_objs, department_objs):
        dep_helper = make_dep_sync_helper(
            CustomTypeList.from_list([CustomDepartment.from_dict(x) for x in department_objs])
        )
        dep_helper.load_to_memory()
        dep_helper.db_sync_manager.sync_type(target_type=Department)

        helper = make_pro_sync_helper(CustomTypeList.from_list([CustomProfile.from_dict(x) for x in dict_objs]))
        helper.load_to_memory()
        helper.db_sync_manager.sync_type(target_type=Profile)
        helper.db_sync_manager.sync_type(target_type=DepartmentThroughModel)
        helper.db_sync_manager.sync_type(target_type=LeaderThroughModel)

        for obj in dict_objs:
            p = Profile.objects.get(category_id=helper.category.id, username=obj["username"])
            assert p
            assert p.code == helper._get_code(obj["code"])
            assert len(p.departments.all().values_list("name", flat=True)) == len(obj["departments"])
