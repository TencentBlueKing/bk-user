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
from bklogin.utils.std_error import APIError, ErrorCode
from django.utils.translation import gettext_lazy


def _format_message(message, exc):
    return f"{exc.code}-{message}"


class TestingErrorCodes:
    foo_bar = ErrorCode("foo message", status_code=500)
    foo_formatted = ErrorCode("foo message", extra_formatter=_format_message)


class TestErrorCode:
    def test_integrated(self):
        error_codes = TestingErrorCodes()
        exc = error_codes.foo_bar

        assert isinstance(exc, APIError)
        assert exc.code == "foo_bar"
        assert exc.status_code == 500  # noqa: PLR2004
        assert exc.message == "foo message"

    def test_formatted(self):
        exc = TestingErrorCodes().foo_formatted
        assert exc.message == "foo_formatted-foo message"

    def test_exception_clone(self):
        error_codes = TestingErrorCodes()
        assert error_codes.foo_bar is not error_codes.foo_bar


class TestAPIError:
    def test_simple_message(self):
        exc = APIError("foo", "foo error", "INVALID_ARGUMENT")
        assert exc.message == "foo error"
        assert exc.code == "foo"

    @pytest.mark.parametrize(
        ("message", "replace", "kwargs", "result"),
        [
            ("", False, {}, "name={name}"),
            ("value", False, {}, "name={name}: value"),
            ("value", False, {"name": "foo"}, "name=foo: value"),
            ("value", True, {"name": "foo"}, "value"),
        ],
    )
    def test_message_format(self, message, replace, result, kwargs):
        exc = APIError("foo", "name={name}")
        exc = exc.format(message=message, replace=replace, **kwargs)
        assert exc.message == result

    def test_format_clone(self):
        exc = APIError("foo", "message")
        formatted_exc = exc.format()
        assert formatted_exc is not exc

    def test_data_property_in_chain(self):
        exc = APIError("foo", "name={name}")
        assert exc.set_data({"value": -1}).f(name="bar").data == {"value": -1}

    def test_lazy_str(self):
        exc = APIError("foo", gettext_lazy("message"))
        formatted_exc = exc.format(gettext_lazy("new message"))
        assert formatted_exc.message == "message: new message"
