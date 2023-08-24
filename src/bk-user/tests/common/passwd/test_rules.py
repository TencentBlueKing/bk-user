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
from bkuser.common.passwd import PasswordRule
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

        assert "密码最小长度不得小于 10 位" in str(e)

    def test_with_min_gt_max_length(self, passwd_rule_cfg):
        """密码最大最小长度冲突"""

        passwd_rule_cfg["min_length"] = 12
        with pytest.raises(ValidationError) as e:
            PasswordRule(**passwd_rule_cfg)

        assert "密码最小长度不得大于最大长度" in str(e)

    def test_without_any_charset(self, passwd_rule_cfg):
        """没有指定任何一个字符集"""

        passwd_rule_cfg["contain_lowercase"] = False
        with pytest.raises(ValidationError) as e:
            PasswordRule(**passwd_rule_cfg)

        assert "至少应该选择小写字母，大写字母，数字，特殊符号中的一个字符集" in str(e)

    def test_set_too_small_not_continuous_count(self, passwd_rule_cfg):
        """设置连续性限制，但阈值过低"""

        passwd_rule_cfg["not_continuous_count"] = 1
        with pytest.raises(ValidationError) as e:
            PasswordRule(**passwd_rule_cfg)

        assert "当设置不允许连续 N 位出现的规则时，该值不可小于 3" in str(e)

    def test_set_not_continuous_count_without_scene(self, passwd_rule_cfg):
        """设置连续性限制，但没有指定场景"""

        passwd_rule_cfg["not_continuous_count"] = 5
        with pytest.raises(ValidationError) as e:
            PasswordRule(**passwd_rule_cfg)

        assert "至少应该选择键盘序，连续字母序，连续数字序，重复字符中的一个场景" in str(e)

    def test_select_scene_without_set_not_continuous_count(self, passwd_rule_cfg):
        """选择场景，但没有设置连续性限制（部分无效配置）"""

        passwd_rule_cfg["not_keyboard_order"] = True
        with pytest.raises(ValidationError) as e:
            PasswordRule(**passwd_rule_cfg)

        assert "需要先设置 [密码不允许连续 N 位出现] 值，才可以选择连续性场景" in str(e)
