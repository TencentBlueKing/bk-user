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
from bkuser.common.passwd import PasswordRule


@pytest.fixture()
def strict_passwd_rule() -> PasswordRule:
    """严格的密码规则"""
    return PasswordRule(
        min_length=24,
        max_length=64,
        contain_lowercase=True,
        contain_uppercase=True,
        contain_digit=True,
        contain_punctuation=True,
        not_continuous_count=3,
        not_keyboard_order=True,
        not_continuous_letter=True,
        not_continuous_digit=True,
        not_repeated_symbol=True,
    )


@pytest.fixture()
def simple_passwd_rule() -> PasswordRule:
    """宽松的密码规则"""
    return PasswordRule(
        min_length=10,
        max_length=20,
        contain_lowercase=True,
        contain_uppercase=False,
        contain_digit=True,
        contain_punctuation=False,
        not_continuous_count=0,
        not_keyboard_order=False,
        not_continuous_letter=False,
        not_continuous_digit=False,
        not_repeated_symbol=False,
    )
