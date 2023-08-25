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
from bkuser.common.passwd import PasswordStrengthError, PasswordValidator


@pytest.fixture()
def strict_validator(strict_passwd_rule) -> PasswordValidator:
    """严格的密码强度校验器，会限制所有规则"""
    return PasswordValidator(strict_passwd_rule)


@pytest.fixture()
def simple_validator(simple_passwd_rule) -> PasswordValidator:
    """简单的密码强度校验器，仅包含少量限制"""
    return PasswordValidator(simple_passwd_rule)


class TestPasswordValidator:
    """密码强度校验器单元测试"""

    def test_validate_length(self, simple_validator, strict_validator):
        password = "1234567890"
        assert simple_validator._validate_length(password) == []
        assert strict_validator._validate_length(password) == ["密码长度至少 24 位"]

        password = "123456789012345678901234567890"
        assert simple_validator._validate_length(password) == ["密码长度至多 20 位"]
        assert strict_validator._validate_length(password) == []

    @pytest.mark.parametrize(
        "password",
        ["pass word123", "ass\tword123", "ass\nword123", "ass\rword123"],
    )
    def test_validate_contains_with_whitespace(self, simple_validator, password):
        """包含空白字符的情况"""
        assert simple_validator._validate_contains(password) == ["密码不能包含空格或空白符号"]

    def test_validate_contains_with_rules(self, simple_validator, strict_validator):
        password = "afftik3487"
        assert simple_validator._validate_contains(password) == []
        assert strict_validator._validate_contains(password) == ["密码必须包含大写字母", "密码必须包含特殊符号"]

        password = "affACPtik3487&^2"
        assert simple_validator._validate_contains(password) == []
        assert strict_validator._validate_contains(password) == []

    @pytest.mark.parametrize(
        ("password", "errors"),
        [
            # 弱密码场景
            ("aaaccc", ["密码强度评级过低"]),
            ("23456789", ["密码强度评级过低"]),
            ("iuytrew", ["密码强度评级过低"]),
            # 强密码场景
            ("aif5ke3co2", []),
            ("aif5&83co2", []),
            ("ai-*5ke3$o2", []),
        ],
    )
    def test_validate_with_zxcvbn_too_lower_score(self, simple_validator, password, errors):
        assert simple_validator._validate_with_zxcvbn(password) == errors

    @pytest.mark.parametrize(
        ("password", "errors"),
        [
            ("qwert12345678-*", ["密码中包含过多的常见单词或弱密码（如：qwert 或 trewq）"]),
            ("trewq123456-*", ["密码中包含过多的常见单词或弱密码（如：qwert 或 trewq）"]),
            ("123456—&qwert", ["密码中包含过多的常见单词或弱密码（如：123456 或 654321）"]),
            # 仅包含单个弱密码词，但是超过阈值
            ("gbome12345678-*", ["密码中包含过多的常见单词或弱密码（如：12345678 或 87654321）"]),
            # 包含弱密码组合，但是没有超过阈值的
            ("trewq*70%20*J&@(123456", []),
            # 使用 leet 映射进行替换的，可以通过检查
            ("qw3rt1847359", []),
        ],
    )
    def test_validate_with_zxcvbn_weak_passwd_combination(self, simple_validator, password, errors):
        assert simple_validator._validate_with_zxcvbn(password) == errors

    def test_validate_with_zxcvbn_continuous(self, simple_validator, strict_validator):
        password = "abCDef234567kkkkk"
        assert simple_validator._validate_with_zxcvbn(password) == []
        assert strict_validator._validate_with_zxcvbn(password) == [
            "密码不可包含 3 位连续字母序（abcdef）",
            "密码不可包含连续 3 位数字序（234567）",
            "密码不可包含 3 位重复字符（k）",
        ]

        password = "ertghnm08354"
        assert simple_validator._validate_with_zxcvbn(password) == []
        assert strict_validator._validate_with_zxcvbn(password) == ["密码不可包含 3 位键盘序（ertghnm）"]

        password = "uricke&239=&2k9d"
        assert simple_validator._validate_with_zxcvbn(password) == []
        assert strict_validator._validate_with_zxcvbn(password) == []

    def test_validate_failed(self, strict_validator):
        password = "ertyu45678AbcDppppppcc "
        ret = strict_validator.validate(password)

        assert ret.ok is False
        assert ret.errors == [
            "密码长度至少 24 位",
            "密码不能包含空格或空白符号",
            "密码必须包含特殊符号",
            "密码不可包含 3 位键盘序（ertyu）",
            "密码不可包含连续 3 位数字序（45678）",
            "密码不可包含 3 位连续字母序（abcd）",
            "密码不可包含 3 位重复字符（p）",
        ]

    def test_validate_failed_and_raise_exception(self, strict_validator):
        password = "abc1234!#"
        with pytest.raises(PasswordStrengthError) as e:
            strict_validator.validate(password, raise_exception=True)

        assert str(e.value) == ", ".join(
            [
                "密码长度至少 24 位",
                "密码必须包含大写字母",
                "密码强度评级过低",
                "密码中包含过多的常见单词或弱密码（如：abc123 或 321cba）",
            ]
        )

    def test_validate_success(self, strict_validator):
        password = "uric8822IOw039x^#ke&239=&2k9d"
        ret = strict_validator.validate(password)

        assert ret.ok is True
        assert ret.errors == []
