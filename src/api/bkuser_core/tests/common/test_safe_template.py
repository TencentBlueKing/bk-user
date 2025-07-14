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

from src.api.bkuser_core.common.safe_template import safe_str_format, BraceOnlyTemplate


class TestBraceOnlyTemplate:
    @pytest.mark.parametrize(
        ("template_str", "kwargs", "expected"),
        [
            # Basic substitution
            ("Hello {name}, welcome to {place}!", {"name": "foo", "place": "bar"}, "Hello foo, welcome to bar!"),
            # Variable inside word
            ("prefix_{var}_suffix", {"var": "test"}, "prefix_test_suffix"),
            # Underscore variable
            ("{underscore_var}", {"underscore_var": "value"}, "value"),
        ],
    )
    def test_various_valid_patterns(self, template_str, kwargs, expected):
        template = BraceOnlyTemplate(template_str)
        assert template.substitute(**kwargs) == expected

    def test_escaped_braces(self):
        # Only "{" needs to be escaped
        template = BraceOnlyTemplate("Use {{ to escape braces, like {{name}")
        assert template.substitute(name="foo") == "Use { to escape braces, like {name}"

    def test_no_substitution_needed(self):
        template = BraceOnlyTemplate("No variables here!")
        assert template.substitute() == "No variables here!"

    def test_missing_variable_raises_error(self):
        template = BraceOnlyTemplate("Hello {name}!")
        with pytest.raises(KeyError):
            template.substitute()


class Test__safe_str_format:
    def test_basic(self):
        assert safe_str_format("Hello {name}!", {"name": "foo"}) == "Hello foo!"

    def test_index_access_should_fail(self):
        with pytest.raises(ValueError, match="Invalid placeholder .*"):
            safe_str_format("Hello {names[0]}!", {"names": "foobar"})
