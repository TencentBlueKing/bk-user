# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
import pytest
from bkuser.common.desensitize import PLACEHOLDER, desensitize_email, desensitize_phone


@pytest.mark.parametrize(
    ("email", "excepted"),
    [
        ("user@example.com", "us****@example.com"),
        ("ab@example.com", "ab****@example.com"),
        ("a@example.com", "a****@example.com"),
        ("this is not an email", "this is not an email"),
        ("", PLACEHOLDER),
    ],
)
def test_desensitize_email(email, excepted):
    assert desensitize_email(email) == excepted


@pytest.mark.parametrize(
    ("phone", "excepted"),
    [
        # 中国大陆
        ("13812345678", "138****5678"),
        ("+8613812345678", "138****5678"),
        # 大陆固定电话
        ("021-12345678", "021-****5678"),
        # 香港
        ("+85212345678", "12****78"),
        # 澳门
        ("+85312345678", "12****78"),
        # 台湾
        ("+886912345678", "91****678"),
        # 海外
        ("+11234567890", "+1****3456****"),
        # 特殊场景
        (" 138 1234 5678 ", "138****5678"),
        (" 138-1234-5678 ", "13****78"),
        ("", PLACEHOLDER),
    ],
)
def test_desensitize_phone(phone, excepted):
    assert desensitize_phone(phone) == excepted
