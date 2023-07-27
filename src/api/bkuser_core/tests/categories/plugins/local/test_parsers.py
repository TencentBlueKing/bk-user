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

from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.categories.plugins.local.exceptions import ParseFailedException
from bkuser_core.categories.plugins.local.parsers import (
    CellParser,
    ColumnParser,
    DepartmentCellParser,
    DepartmentColumnParser,
    EmailCellParser,
    LeadersCellParser,
    PhoneNumberParser,
    UsernameCellParser,
)
from bkuser_core.tests.departments.utils import make_departments_by_full_path
from bkuser_core.tests.utils import make_simple_profile

pytestmark = pytest.mark.django_db


class TestDepartmentCellParser:
    @pytest.fixture
    def local_category(self):
        return ProfileCategory.objects.create(type=CategoryType.LOCAL.value, display_name="Test", domain="test.com")

    @pytest.fixture
    def cell_parser(self, local_category):
        return DepartmentCellParser(local_category.id)

    def test_simple_find_department(self, local_category, cell_parser):
        make_departments_by_full_path(["A", "B", "C"], local_category.id)

        d = cell_parser.parse_to_db_obj("A/B/C")
        d = list(d)
        assert d[0].name == "C"

    def test_multiple_name_department(self, local_category, cell_parser):
        make_departments_by_full_path(["A", "B", "C", "D"], local_category.id)
        make_departments_by_full_path(["A", "B", "C", "E"], local_category.id)

        d = cell_parser.parse_to_db_obj("A/B/C/D")
        d = list(d)
        assert d[0].name == "D"

    @pytest.mark.parametrize(
        "full_paths, case, expected",
        [
            (
                [["A", "B", "C", "D"], ["A", "B", "C", "E"], ["F", "B", "C", "E"]],
                "A/B/C/D\nA/B/C/E",
                ["D", "E"],
            ),
            (
                [["A", "B", "C", "D"], ["A", "B", "C", "E"], ["F", "B", "C", "E"]],
                "A/B/C/D;F/B/C/E",
                ["D", "E"],
            ),
            (
                [["A", "B", "C", "D"], ["A", "B", "C", "E"], ["F", "B", "C", "E"]],
                "A/B/C/D,A/B/C/E",
                ["D", "E"],
            ),
            (
                [["A", "B", "C", "D"], ["A", "B", "C", "E"], ["F", "B", "C"]],
                "A/B/C/D,F/B/C",
                ["D", "C"],
            ),
        ],
    )
    def test_multiple_departments(self, local_category, cell_parser, full_paths, case, expected):
        for f in full_paths:
            make_departments_by_full_path(f, local_category.id)

        d = cell_parser.parse_to_db_obj(case)
        d = list(d)
        assert d[0].name == expected[0]
        assert d[1].name == expected[1]

    def test_wrong_split(self, cell_parser):
        assert cell_parser.parse("") == {"department_name": []}

        with pytest.raises(ParseFailedException):
            cell_parser.parse([1])  # noqa


class TestPhoneNumberParser:
    @pytest.mark.parametrize(
        "case, expected",
        [
            ("+8612341234123", ("86", "12341234123")),
            ("+1123456", ("1", "123456")),
            ("+442079813000", ("44", "2079813000")),
            ("+1212341234123", ("1", "212341234123")),
        ],
    )
    def test_parse_country(self, case, expected):
        r = PhoneNumberParser(1).parse(case)
        assert expected == (r["country_code"], r["telephone"])

    @pytest.mark.parametrize(
        "case, expected",
        [
            ("+8612341234123", ("CN", "12341234123")),
            ("+1123456", ("US", "123456")),
            ("+442079813000", ("GB", "2079813000")),
            ("+1212341234123", ("US", "212341234123")),
        ],
    )
    def test_parse_iso(self, case, expected):
        r = PhoneNumberParser(1).parse(case)
        assert expected == (r["iso_code"], r["telephone"])

    def test_parse_empty(self):
        with pytest.raises(ParseFailedException):
            PhoneNumberParser(1).parse("")

    @pytest.mark.parametrize(
        "case",
        [
            "+",
            "12345",
            "1300000000012",
        ],
    )
    def test_parse_exception(self, case):
        with pytest.raises(ParseFailedException):
            PhoneNumberParser(1).parse(case)


class TestEmailParser:
    @pytest.mark.parametrize(
        "case, expected",
        [
            ("abc@xyz.com", ({"email": "abc@xyz.com"})),
            ("123@xyz.com", ({"email": "123@xyz.com"})),
            ("test@example.net", ({"email": "test@example.net"})),
        ],
    )
    def test_normal_email(self, case, expected):
        r = EmailCellParser(1).parse(case)
        assert expected == r

    def test_parse_empty(self):
        with pytest.raises(ParseFailedException):
            EmailCellParser(1).parse("")

    @pytest.mark.parametrize(
        "case",
        [
            "123@",
            "123",
            "123.com",
        ],
    )
    def test_parse_exception(self, case):
        with pytest.raises(ParseFailedException):
            EmailCellParser(1).parse(case)


class TestLeadersCellParser:
    @pytest.mark.parametrize(
        "case, expected",
        [
            ("user01,user02,xxx,", ["user01", "user02", "xxx"]),
            ("aaa", ["aaa"]),
            ("user01, dddd,,", ["user01", "dddd"]),
            ("user01;dddd,,", ["user01", "dddd"]),
            ("user01;dddd,ddd\nqqq", ["user01", "dddd", "ddd", "qqq"]),
            ("", []),
        ],
    )
    def test_parse(self, case, expected):
        def get_targets(name_list):

            for i in name_list:
                yield make_simple_profile(username=i)

        assert list(get_targets(expected)) == list(LeadersCellParser(1).parse_to_db_obj(case))

    def test_parse_empty(self):
        assert LeadersCellParser(1).parse("") == {"leader": []}


class TestUsernameParser:
    @pytest.mark.parametrize(
        "case, expected",
        [
            ["asdf", "asdf"],
            ["123...", "123..."],
        ],
    )
    def test_parse(self, case, expected):
        assert expected == UsernameCellParser(1).parse(case)["username"]

    @pytest.mark.parametrize(
        "case",
        [
            "-asdf",
            ".asdf",
            "asdf@asdf",
        ],
    )
    def test_parse_raise(self, case):
        with pytest.raises(ParseFailedException):
            UsernameCellParser(1).parse(case)


class TestDepartmentColumnParser:
    @pytest.mark.parametrize(
        "case,expected",
        [
            (["A/B/C/D\nA/B/C/E"], [["A", "B", "C", "D"], ["A", "B", "C", "E"]]),
            (
                ["A/B/C/D;A/B/C/E", "A/B/C/D\nA/B/C/R"],
                [["A", "B", "C", "D"], ["A", "B", "C", "E"], ["A", "B", "C", "R"]],
            ),
            (
                ["A/B/C/D;A/B/C/E", ""],
                [["A", "B", "C", "D"], ["A", "B", "C", "E"]],
            ),
        ],
    )
    def test_parse(self, case, expected):
        assert DepartmentColumnParser(1).parse(case) == expected


class TestBase:
    def test_base(self):
        with pytest.raises(NotImplementedError):
            CellParser(1).parse("fake")

        with pytest.raises(NotImplementedError):
            CellParser(1).parse_to_db_obj("fake")

        with pytest.raises(NotImplementedError):
            ColumnParser(1).parse([])
