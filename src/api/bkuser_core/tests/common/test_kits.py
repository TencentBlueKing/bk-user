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
from bkuser_core.common.kits import convert_camelcase, convert_camelcase_dict

from bkuser_global.utils import force_str_2_bool


class TestKits:
    @pytest.mark.parametrize(
        "case,result",
        [
            ("startsAt", "starts_at"),
            ("StartsAt", "starts_at"),
            ("starts_at", "starts_at"),
        ],
    )
    def test_convert_name(self, case, result):
        assert convert_camelcase(case) == result

    def test_convert_dict(self):
        camel_case_dict = {"CamelCase": 1, "lowerCamelCase": 2, "snake_case": 3}
        assert convert_camelcase_dict(camel_case_dict) == {
            "camel_case": 1,
            "lower_camel_case": 2,
            "snake_case": 3,
        }

    @pytest.mark.parametrize(
        "case,expected",
        [
            ("false", False),
            ("true", True),
            ("False", False),
            ("True", True),
            (True, True),
            (False, False),
            ("0", False),
            ("1", True),
        ],
    )
    def test_force_str_to_bool(self, case, expected):
        assert force_str_2_bool(case) == expected

    @pytest.mark.parametrize("case,expected", [("aaaa", False), (2, False), (None, False)])
    def test_force_str_to_bool_raise(self, case, expected):
        assert force_str_2_bool(case) == expected
        with pytest.raises(ValueError):
            force_str_2_bool(case, True)
