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

from .constants import COMMON_TITLES
from bkuser_core.categories.plugins.local.client import ExcelHelper
from bkuser_core.categories.plugins.local.exceptions import ParseFailedException
from bkuser_core.categories.plugins.local.syncer import ExcelSyncer, GeneralParser, ParserSet
from bkuser_core.departments.models import Department
from bkuser_core.profiles.constants import DynamicFieldTypeEnum
from bkuser_core.profiles.models import DynamicFieldInfo, Profile
from bkuser_core.tests.utils import make_simple_department, make_simple_profile

pytestmark = pytest.mark.django_db


class TestExcelSyncer:
    @pytest.fixture
    def syncer(self, local_category):
        return ExcelSyncer(category_id=local_category.id)

    @pytest.fixture
    def make_parser_set(self, local_category):
        def _parser_set(titles):
            return ParserSet.from_classes(local_category.id, titles=titles)

        return _parser_set

    @pytest.mark.parametrize(
        "department_groups,count, expected",
        [
            ([["A", "B", "C"], ["E", "B", "F"]], 6, {"A", "B", "C", "E", "F"}),
            ([["A", "B", "C"], ["A", "B", "C"]], 3, {"A", "B", "C"}),
            ([["A", "B", "C"], ["O", "B", "C"]], 6, {"A", "O", "B", "C"}),
        ],
    )
    def test_sync_departments(self, syncer, department_groups, count, expected):
        """测试部门同步"""
        syncer._sync_departments(department_groups)
        assert (
            set(Department.objects.filter(category_id=syncer.category_id).values_list("name", flat=True)) == expected
        )
        assert Department.objects.filter(category_id=syncer.category_id).count() == count

        for g in department_groups:
            parent = None
            for d in g:
                parent = Department.objects.get(name=d, parent=parent)
                assert parent

    @pytest.mark.parametrize(
        "pre_create_department,users,titles,expected",
        [
            (
                ["A", "B", "C"],
                [
                    [*["aaaa"] * 2, "aaaa@test.com", "13000000000", *["aaaa"] * 2, ""],
                    [*["bbbb"] * 2, "bbbb@test.com", "13000000001", *["bbbb"] * 2, "A/B/C"],
                ],
                COMMON_TITLES,
                {"aaaa", "bbbb"},
            ),
            (
                ["A", "B", "C"],
                [
                    [*["aaaa"] * 2, "bbbb@test.com", "13000000000", *["aaaa"] * 2, "", "ddd"],
                    [*["bbbb"] * 2, "bbbb@test.com", "13000000000", *["bbbb"] * 2, "A/B/C", "qqq"],
                    [*["cccc"] * 2, "cccc@test.com", "13000000000", *["cccc"] * 2, "A/B/C", ""],
                ],
                [*COMMON_TITLES, "自定义字段1"],
                {"aaaa", "bbbb", "cccc"},
            ),
        ],
    )
    def test_sync_users(self, syncer, pre_create_department, users, make_parser_set, titles, expected):
        """测试用户同步"""
        DynamicFieldInfo.objects.create(
            type=DynamicFieldTypeEnum.ONE_ENUM.value,
            name="custom-field1",
            options=[["1", "ddd"], ["2", "qqq"]],
            order=10,
            display_name="自定义字段1",
        )
        parent_department = None
        for i in pre_create_department:
            parent_department = make_simple_department(
                name=i,
                force_create_params={
                    "parent": parent_department,
                    "category_id": syncer.category_id,
                },
            )

        syncer._sync_users(make_parser_set(titles), users)
        assert (
            set(Profile.objects.filter(category_id=syncer.category_id).values_list("username", flat=True)) == expected
        )

    @pytest.mark.parametrize(
        "users,titles,expected,is_overwrite",
        [
            (
                [
                    [*["aaaa"] * 2, "xxxx@xxxx.xyz", "13000000000", *["aaaa"] * 2, ""],
                    [*["bbbb"] * 2, "xxxx@xxxx.xyz", "13000000000", *["bbbb"] * 2, ""],
                ],
                COMMON_TITLES,
                {
                    "aaaa": "xxxx@xxxx.xyz",
                    "bbbb": "xxxx@xxxx.xyz",
                    "cccc": "cccc@xxxx.com",
                },
                True,
            )
        ],
    )
    def test_update_existed_users(self, syncer, users, make_parser_set, titles, expected, is_overwrite):
        """测试更新已存在用户"""
        for u in ["aaaa", "cccc"]:
            a = make_simple_profile(username=u, force_create_params={"category_id": syncer.category_id})
            a.email = f"{u}@xxxx.com"
            a.save()

        # TODO: 当前 id 最大值是在 db_sync_manager 初始化时确定的，实际上并不科学
        syncer.db_sync_manager._update_cache()
        syncer._sync_users(make_parser_set(titles), users, is_overwrite=is_overwrite)
        for k, v in expected.items():
            assert Profile.objects.get(category_id=syncer.category_id, username=k).email == v

    @pytest.mark.parametrize(
        "users,titles,expected,leader_expected",
        [
            (
                [
                    [*["aaaa"] * 2, "aaaa@test.com", "13000000000", *["aaaa"] * 2, "", ""],
                    [*["bbbb"] * 2, "bbbb@test.com", "13000000000", *["bbbb"] * 2, "", "aaaa"],
                ],
                [*COMMON_TITLES, "上级"],
                {"aaaa", "bbbb"},
                {"bbbb": {"aaaa"}},
            ),
        ],
    )
    def test_sync_leaders(self, syncer, users, make_parser_set, titles, expected, leader_expected):
        """测试用户同步"""
        syncer._sync_users(make_parser_set(titles), users)
        syncer._sync_leaders(make_parser_set(titles), users)
        assert (
            set(Profile.objects.filter(category_id=syncer.category_id).values_list("username", flat=True)) == expected
        )

        for k, v in leader_expected.items():
            assert set(Profile.objects.get(username=k).leader.all().values_list("username", flat=True)) == v

    @pytest.mark.parametrize(
        "users,titles,expected",
        [
            (
                [
                    ["aaaa", *[""] * 6, ""],
                ],
                COMMON_TITLES,
                set(),
            ),
            (
                [
                    [*["aaaa"] * 6, ""],
                    ["bbbb", "some-name", *[""] * 4, ""],
                    ["cccc", "some-name", "email", *[""] * 3, ""],
                ],
                COMMON_TITLES,
                {"aaaa"},
            ),
        ],
    )
    def test_sync_wrong_users(self, syncer, users, make_parser_set, titles, expected):
        """测试异常用户同步"""
        # FIXME: assert exception
        with pytest.raises(Exception) as exc_info:
            syncer._sync_users(make_parser_set(titles), users)
        assert (
            "导入执行完成: 成功 0 条记录, 失败 3 条记录" in exc_info.value.args[0]
            or "导入执行完成: 成功 0 条记录, 失败 1 条记录" in exc_info.value.args[0]
        )


class TestParserSet:
    @pytest.fixture
    def excel_helper(self):
        return ExcelHelper()

    @pytest.mark.parametrize(
        "titles,extras",
        [
            (["全名", "在职状态", "组织", "QQ", "职务", "AAA"], ["AAA", "BBB"]),
            (["全名", "在职状态", "组织", "QQ", "职务"], []),
        ],
    )
    def test_init_from_classes(self, excel_helper, titles, extras):
        """测试初始化"""
        for e in extras:
            DynamicFieldInfo.objects.create(name=e, display_name=e, order=1)

        ps = ParserSet.from_classes(category_id=1, titles=titles)

        assert [x.display_name for x in ps.fields.values()] == titles

    @pytest.mark.parametrize(
        "titles",
        [
            ["未知", "全名", "用户名"],
            ["", "全名", "用户名"],
        ],
    )
    def test_init_from_classes_unknown(self, excel_helper, titles):
        """测试初始化"""
        with pytest.raises(ValueError):
            ParserSet.from_classes(category_id=1, titles=titles)

    @pytest.mark.parametrize(
        "titles, key, row_data, expected",
        [
            (
                ["全名", "在职状态", "组织", "QQ", "职务"],
                "display_name",
                ["AAA", "BBB", "CCC", "DDD"],
                "AAA",
            ),
            (["全名", "QQ", "职务"], "qq", ["BBB", "CCC", "DDD"], "CCC"),
            (
                ["全名", "在职状态", "组织", "QQ"],
                "staff_status",
                ["AAA", "在职", "CCC", "DDD"],
                "IN",
            ),
            (
                ["全名", "在职状态", "组织", "QQ"],
                "department_name",
                ["AAA", "在职", "CCC/WWW/FFF,LLL", "DDD"],
                [["CCC", "WWW", "FFF"], ["LLL"]],
            ),
            (
                ["全名", "上级", "组织", "QQ"],
                "leader",
                ["AAA", "xx,ddd,fff", "CCC/WWW/FFF,LLL", "DDD"],
                ["xx", "ddd", "fff"],
            ),
        ],
    )
    def test_parse_key(self, excel_helper, titles, key, row_data, expected):
        ps = ParserSet.from_classes(category_id=1, titles=titles)
        assert ps.parse_key(key, row_data)[key] == expected

    @pytest.mark.parametrize(
        "titles, skip_keys, row_data, expected",
        [
            (
                ["全名", "在职状态", "组织", "QQ", "职务"],
                [],
                ["AAA", "离职", "CCC", "DDD", "员工"],
                {
                    "display_name": "AAA",
                    "staff_status": "OUT",
                    "department_name": [["CCC"]],
                    "qq": "DDD",
                    "position": 0,
                    "extras": {},
                },
            ),
        ],
    )
    def test_parse_row(self, excel_helper, titles, skip_keys, row_data, expected):
        ps = ParserSet.from_classes(category_id=1, titles=titles)
        assert ps.parse_row(row_data, skip_keys=skip_keys) == expected


class TestGeneralParser:
    @pytest.mark.parametrize(
        "builtin,type,options,raw_content,expected,default",
        [
            (
                True,
                DynamicFieldTypeEnum.ONE_ENUM.value,
                [["aaa", "AAA"], ["bbb", "BBB"]],
                "BBB",
                "bbb",
                ["aaa"],
            ),
            (
                False,
                DynamicFieldTypeEnum.ONE_ENUM.value,
                [["aaa", "AAA"], ["bbb", "BBB"]],
                "AAA",
                "aaa",
                [],
            ),
            (
                False,
                DynamicFieldTypeEnum.ONE_ENUM.value,
                [[0, "AAA"], ["bbb", "BBB"]],
                "AAA",
                0,
                [],
            ),
            (False, DynamicFieldTypeEnum.ONE_ENUM.value, [], "AAA", "AAA", []),
            (True, DynamicFieldTypeEnum.ONE_ENUM.value, [], "AAA", "AAA", []),
            (
                True,
                DynamicFieldTypeEnum.ONE_ENUM.value,
                [["aaa", "AAA"]],
                "bbb",
                "CCC",
                "CCC",
            ),
            (
                True,
                DynamicFieldTypeEnum.MULTI_ENUM.value,
                [["aaa", "AAA"], ["bbb", "BBB"], ["ccc", "CCC"]],
                "AAA,BBB",
                ["aaa", "bbb"],
                [],
            ),
            (
                True,
                DynamicFieldTypeEnum.MULTI_ENUM.value,
                [["aaa", "AAA"], ["bbb", "BBB"], ["ccc", "CCC"]],
                "XXX,YYY",
                ["aaa", "bbb"],
                ["aaa", "bbb"],
            ),
            (
                True,
                DynamicFieldTypeEnum.MULTI_ENUM.value,
                [[0, "AAA"], ["bbb", "BBB"], ["ccc", "CCC"]],
                "",
                [0, "bbb"],
                [0, "bbb"],
            ),
        ],
    )
    def test_parse(self, builtin, type, options, raw_content, expected, default):
        f = DynamicFieldInfo.objects.create(
            name="test",
            type=type,
            default=default,
            builtin=builtin,
            options=options,
            order=1,
        )

        assert GeneralParser(f).parse(raw_content)["test"] == expected

    @pytest.mark.parametrize(
        "builtin,type,options,raw_content,default",
        [
            (True, DynamicFieldTypeEnum.ONE_ENUM.value, [["aaa", "AAA"]], "bbb", ""),
            (
                True,
                DynamicFieldTypeEnum.MULTI_ENUM.value,
                [["aaa", "AAA"], ["bbb", "BBB"], ["ccc", "CCC"]],
                "XXX,YYY",
                [],
            ),
            (
                True,
                DynamicFieldTypeEnum.MULTI_ENUM.value,
                [["aaa", "AAA"], ["bbb", "BBB"], ["ccc", "CCC"]],
                "aaa,bbb",
                [],
            ),
        ],
    )
    def test_parse_raise(self, builtin, type, options, raw_content, default):
        f = DynamicFieldInfo.objects.create(
            name="test",
            type=type,
            default=default,
            builtin=builtin,
            options=options,
            order=1,
        )

        with pytest.raises(ParseFailedException):
            GeneralParser(f).parse(raw_content)

        try:
            GeneralParser(f).parse(raw_content)
        except Exception as e:  # pylint: disable=broad-except
            assert str(e).startswith("解析字段 test 失败:")

    @pytest.mark.parametrize(
        "require,f_type,raw_content,default,options,expected",
        [
            (True, DynamicFieldTypeEnum.STRING.value, "", "", {}, ParseFailedException),
            (True, DynamicFieldTypeEnum.NUMBER.value, "", "asdf", {}, {"test": "asdf"}),
            (
                True,
                DynamicFieldTypeEnum.MULTI_ENUM.value,
                "CCCC",
                "cccc",
                [["cccc", "CCCC"]],
                {"test": ["cccc"]},
            ),
            (
                True,
                DynamicFieldTypeEnum.ONE_ENUM.value,
                "CCCC",
                "cccc",
                [["cccc", "CCCC"]],
                {"test": "cccc"},
            ),
            (True, DynamicFieldTypeEnum.STRING.value, 0, "aaaa", [], {"test": 0}),
            (True, DynamicFieldTypeEnum.STRING.value, "", 0, [], {"test": 0}),
            (True, DynamicFieldTypeEnum.STRING.value, "", [], [], ParseFailedException),
            (False, DynamicFieldTypeEnum.STRING.value, "", "", {}, {}),
        ],
    )
    def test_parse_require(self, require, f_type, raw_content, default, options, expected):
        f = DynamicFieldInfo.objects.create(
            name="test",
            type=f_type,
            default=default,
            options=options,
            require=require,
            order=1,
        )

        if isinstance(expected, type) and issubclass(expected, Exception):
            with pytest.raises(expected):
                GeneralParser(f).parse(raw_content)
        else:
            assert GeneralParser(f).parse(raw_content) == expected
