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
from unittest.mock import patch

import pytest
from django.contrib.auth.hashers import check_password

from bkuser_core.audit.utils import create_profile_log
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.profiles.exceptions import CountryISOCodeNotMatch, UsernameWithDomainFormatError
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.utils import (
    align_country_iso_code,
    check_former_passwords,
    make_password_by_config,
    parse_username_domain,
)
from bkuser_core.user_settings.constants import InitPasswordMethod
from bkuser_core.user_settings.models import Setting

pytestmark = pytest.mark.django_db


class TestParseUsername:
    @pytest.mark.parametrize(
        "raw_username, known_domain, expected_username",
        [
            # 包含 未知字符 $
            ("user-67@asdfads.com", "asdfads.com", "user-67"),
            ("user-67@fdfdf", "fdfdf", "user-67"),
            ("us_er-67@fdfdf", "fdfdf", "us_er-67"),
            ("us.er-67@fdfdf", "fdfdf", "us.er-67"),
        ],
    )
    def test_normal_domain_username(self, raw_username, known_domain, expected_username):
        username, domain = parse_username_domain(raw_username)

        assert username == expected_username
        assert domain == known_domain

    @pytest.mark.parametrize(
        "raw_username",
        ["user-$67@fdfdf", "user?-67@fdfdfd", "user-67@_fdfdfd", "user-67@@fdfdfd"],
    )
    def test_wrong_domain_username(self, raw_username):
        """测试在不传入已知域名的情况下格式错误"""
        with pytest.raises(UsernameWithDomainFormatError):
            parse_username_domain(raw_username)

    @pytest.mark.parametrize(
        "raw_username, known_domain, expected_username",
        [
            # 包含 未知字符 $
            ("user-67@asdfads.com", "asdfads.com", "user-67"),
            ("user-67@fdfdf", "fdfdf", "user-67"),
            ("us_er-67@fdfdf", "fdfdf", "us_er-67"),
            ("us.er-67@fdfdf", "fdfdf", "us.er-67"),
        ],
    )
    def test_known_domain_username(self, raw_username, known_domain, expected_username):
        """测试当已知domain 和用户名时能正确解析"""
        username, domain = parse_username_domain(raw_username, known_domain)
        assert username == expected_username
        assert known_domain == domain

    @pytest.mark.parametrize(
        "raw_username, known_domain",
        [
            # 包含 未知字符 $
            ("user-67@fdfdfd", "abcd"),
            ("user$-67@fdfdfd", "abcd"),
            ("user?-67@fdfdfd", "abcd"),
            ("user-67@_fdfdfd", "abcd"),
        ],
    )
    def test_wrong_known_domain_username(self, raw_username, known_domain):
        with pytest.raises(ValueError):
            parse_username_domain(raw_username, known_domain)

    def test_no_domain_in_username(self):
        raw_username = "user-67"
        known_domain = "fdfdf"

        with pytest.raises(ValueError):
            parse_username_domain(raw_username, known_domain)


class TestAlignCountryISOCode:
    @pytest.mark.parametrize(
        "pass_in, pass_out",
        [
            (("86", "CN"), ("86", "CN")),
            (("86", "cn"), ("86", "CN")),
            (("1", "US"), ("1", "US")),
            (("1", "us"), ("1", "US")),
            (("0", "zz"), ("86", "CN")),
        ],
    )
    def test_both_pass_in(self, pass_in, pass_out):
        """测试正常传入--对齐检测逻辑"""

        a, b = align_country_iso_code(pass_in[0], pass_in[1])
        assert a == pass_out[0]
        assert b == pass_out[1]

    def test_only_country_code(self):
        """测试只传入 country code"""
        country_code = "86"

        a, b = align_country_iso_code(country_code, "")
        assert a == "86"
        assert b == "CN"

    @pytest.mark.parametrize(
        "iso_code, expected",
        [
            ("cn", ("86", "CN")),
            ("CN", ("86", "CN")),
            ("zz", ("86", "CN")),
            ("us", ("1", "US")),
            ("asdfasdf", ("86", "CN")),
        ],
    )
    def test_only_iso_code(self, iso_code, expected):
        """测试只传入 iso code"""
        a, b = align_country_iso_code("", iso_code)
        assert a == expected[0]
        assert b == expected[1]

    @pytest.mark.parametrize("iso_code", ["ioio", "ZZ"])
    def test_invalid_iso_code(self, iso_code):
        """测试传入非法 iso code"""
        a, b = align_country_iso_code("", iso_code)
        assert a == "86"
        assert b == "CN"

    def test_no_input(self):
        """测试传入空值异常"""
        with pytest.raises(ValueError):
            align_country_iso_code("", "")

    @pytest.mark.parametrize(
        "wrong_pair",
        [
            ("86", "US"),
            ("999", "ZZ"),
        ],
    )
    def test_align(self, wrong_pair):
        """测试不匹配异常"""
        with pytest.raises(CountryISOCodeNotMatch):
            align_country_iso_code(wrong_pair[0], wrong_pair[1])


class TestMakePassword:
    FAKE_RANDOM_PASSWORD = "abcdefg"

    def make_fake_category(self, init_config: dict) -> ProfileCategory:
        c = ProfileCategory.objects.create(display_name="Fake", domain="fake", type="local")
        c.make_default_settings()

        for k, v in init_config.items():
            s = Setting.objects.get(category_id=c.pk, meta__key=k)
            s.value = v
            s.save()

        return c

    @pytest.mark.parametrize(
        "init_method,init_password,return_raw,expected",
        [
            (
                InitPasswordMethod.FIXED_PRESET.value,
                "aaaaaa",
                True,
                ("aaaaaa", False),
            ),
            (
                InitPasswordMethod.FIXED_PRESET.value,
                "aaaaaa",
                False,
                ("aaaaaa", False),
            ),
            (
                InitPasswordMethod.RANDOM_VIA_MAIL.value,
                "bbbbbb",
                True,
                (FAKE_RANDOM_PASSWORD, True),
            ),
            (
                InitPasswordMethod.RANDOM_VIA_MAIL.value,
                "bbbbbb",
                False,
                (FAKE_RANDOM_PASSWORD, True),
            ),
        ],
    )
    def test_make_password(self, init_method, init_password, return_raw, expected):
        c = self.make_fake_category({"init_password": init_password, "init_password_method": init_method})

        with patch("bkuser_core.profiles.utils.gen_password") as mocked_password:
            mocked_password.return_value = self.FAKE_RANDOM_PASSWORD
            if return_raw:
                assert make_password_by_config(c.pk, True) == expected
            else:
                encrypted, should_notify = make_password_by_config(c.pk, False)
                check_password(expected[0], encrypted)
                assert should_notify == expected[1]


class TestCheckFormerPasswords:
    @pytest.mark.parametrize(
        "former_passwords,new_password,max_history,expected",
        [
            (["aaaa", "vvvv", "cccc"], "cccc", 3, True),
            (["aaaa", "vvvv", "cccc"], "cccc", 2, True),
            (["aaaa", "vvvv", "cccc"], "bbbb", 3, False),
            (["aaaa", "vvvv", "cccc"], "aaaa", 2, False),
            (["aaaa"], "aaaa", 3, True),
        ],
    )
    def test_in(self, former_passwords, new_password, max_history, expected):
        """if new password in former passwords"""
        p = Profile.objects.get(id=1)
        for pwd in former_passwords:
            create_profile_log(p, "ResetPassword", {"is_success": True, "password": pwd})

        assert check_former_passwords(p, new_password, max_history) == expected
