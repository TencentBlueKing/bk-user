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
from bkuser.common.passwd import PasswordGenerateError, PasswordGenerator


class TestPasswordGenerator:
    """密码生成器单元测试"""

    def test_generate_with_strict_passwd_rule(self, strict_passwd_rule):
        # PasswordGenerator 内置 PasswordValidator，因此此处检查确实生成了密码即可
        password = PasswordGenerator(strict_passwd_rule).generate()
        assert password != ""

    def test_generate_with_simple_passwd_rule(self, simple_passwd_rule):
        # PasswordGenerator 内置 PasswordValidator，因此此处检查确实生成了密码即可
        password = PasswordGenerator(simple_passwd_rule).generate()
        assert password != ""

    def test_generate_with_bad_passwd_rule(self, strict_passwd_rule):
        """限制只使用六位的密码，但是有诸多的限制，导致无法生成可行的密码"""
        strict_passwd_rule.min_length = 6
        strict_passwd_rule.max_length = 6

        with pytest.raises(PasswordGenerateError):
            PasswordGenerator(strict_passwd_rule).generate()
