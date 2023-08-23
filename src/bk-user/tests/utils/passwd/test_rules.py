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
from typing import Dict

import pytest
from bkuser.utils.passwd import PasswordRule
from pydantic import ValidationError


@pytest.fixture()
def passwd_rule_cfg() -> Dict:
    return {
        "min_length": 10,
        "max_length": 10,
        "contain_lowercase": True,
        "contain_uppercase": False,
        "contain_digit": False,
        "contain_punctuation": False,
        "not_continuous_count": 0,
        "not_keyboard_order": False,
        "not_continuous_letter": False,
        "not_continuous_digit": False,
        "not_repeated_symbol": False,
    }


class TestPasswordRule:
    """测试密码规则"""

    def test_with_simple_cfg(self, passwd_rule_cfg):
        """简单的密码规则"""
        assert PasswordRule(**passwd_rule_cfg)

    def test_with_strict_cfg(self):
        """严格的密码规则"""
        rule_cfg: Dict = {
            "min_length": 24,
            "max_length": 64,
            "contain_lowercase": True,
            "contain_uppercase": True,
            "contain_digit": True,
            "contain_punctuation": True,
            "not_continuous_count": 3,
            "not_keyboard_order": True,
            "not_continuous_letter": True,
            "not_continuous_digit": True,
            "not_repeated_symbol": True,
        }

        rule = PasswordRule(**rule_cfg)
        assert rule is not None

    def test_with_too_small_min_length(self, passwd_rule_cfg):
        """密码最小长度过小"""

        passwd_rule_cfg["min_length"] = 1
        with pytest.raises(ValidationError) as e:
            PasswordRule(**passwd_rule_cfg)

        assert "min_length must be greater than or equal to" in str(e)

    def test_with_min_gt_max_length(self, passwd_rule_cfg):
        """密码最大最小长度冲突"""

        passwd_rule_cfg["min_length"] = 12
        with pytest.raises(ValidationError) as e:
            PasswordRule(**passwd_rule_cfg)

        assert "min_length cannot greater than max_length" in str(e)

    def test_without_any_charset(self, passwd_rule_cfg):
        """没有指定任何一个字符集"""

        passwd_rule_cfg["contain_lowercase"] = False
        with pytest.raises(ValidationError) as e:
            PasswordRule(**passwd_rule_cfg)

        assert "at least one of contain_lowercase" in str(e)

    def test_set_too_small_not_continuous_count(self, passwd_rule_cfg):
        """设置连续性限制，但阈值过低"""

        passwd_rule_cfg["not_continuous_count"] = 1
        with pytest.raises(ValidationError) as e:
            PasswordRule(**passwd_rule_cfg)

        assert "not_continuous_count cannot less than" in str(e)

    def test_set_not_continuous_count_without_scene(self, passwd_rule_cfg):
        """设置连续性限制，但没有指定场景"""

        passwd_rule_cfg["not_continuous_count"] = 5
        with pytest.raises(ValidationError) as e:
            PasswordRule(**passwd_rule_cfg)

        assert "at least one of not_keyboard_order, not_continuous_letter" in str(e)
