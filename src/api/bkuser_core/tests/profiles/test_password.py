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
from rest_framework.exceptions import ValidationError

from bkuser_core.profiles.password import PasswordValidator


class TestPasswordValidate:
    @pytest.mark.parametrize(
        "include_elements,test_case",
        [
            (["upper"], "DDDD"),
            (["lower"], "dddd"),
            (["upper", "lower"], "ddDDDi"),
            (["int"], "33DDDD"),
            (["upper", "special"], ";8dDDD"),
            (["upper", "special"], "-8dDDD"),
            (["lower", "special"], "dd*@11"),
            (["lower", "int"], "1dD*"),
            (["lower", "int", "special", "upper"], "1dD*"),
        ],
    )
    def test_include(self, include_elements, test_case):
        pv = PasswordValidator(
            max_length=6, min_length=4, include_elements=include_elements, exclude_elements_config={}
        )
        pv.validate(test_case)

    @pytest.mark.parametrize(
        "include_elements,test_case",
        [
            # 即使包含，但是超长
            (["upper"], "dDDdfaslkj;;lkjl89798761"),
            # 即使包含，但是过短
            (["upper"], "DD"),
            # 一种未命中
            (["lower", "special"], "DDDDDD"),
            (["int"], "ddDDDD*&&KDkfajsl"),
            (["special"], "dfasdf787871DDD"),
            # 两种命中一种
            (["lower", "special"], "DdkfaljkljD"),
            # 两种命中一种
            (["int", "special"], "Ddkfa88ljD"),
            # 三种命中两种
            (["int", "special", "upper"], "Ddkfa88ljD"),
        ],
    )
    def test_include_fail(self, include_elements, test_case):
        pv = PasswordValidator(
            max_length=6, min_length=4, include_elements=include_elements, exclude_elements_config={}
        )
        with pytest.raises(ValidationError):
            pv.validate(test_case)

    @pytest.mark.parametrize(
        "include_elements,exclude_elements,max_length,test_case",
        [
            (["lower"], ["alphabet_seq", "special_seq", "num_seq"], 3, "a@#b12dc*(12&*"),
            (["lower"], ["alphabet_seq", "special_seq", "num_seq", "duplicate_char"], 3, "ab@#bb122ddc*(112&**"),
        ],
    )
    def test_exclude(self, include_elements, exclude_elements, max_length, test_case):

        # 由于指定了 custom_regex，这里的长度和内置验证规则不再生效
        pv = PasswordValidator(
            max_length=20,
            min_length=4,
            include_elements=include_elements,
            exclude_elements_config={e: max_length for e in exclude_elements},
        )
        pv.validate(test_case)

    @pytest.mark.parametrize(
        "include_elements,exclude_elements,max_length,test_case",
        [
            (["lower"], ["alphabet_seq"], 3, "ABcd"),
            (["lower"], ["alphabet_seq"], 2, "abdc"),
            (["lower"], ["special_seq"], 3, "qwfasd^&*asd"),
            (["lower"], ["special_seq"], 3, "!@#132Qss5"),
            (["lower"], ["keyboard_seq"], 3, "asdfjfudieasdf"),
            (["lower"], ["keyboard_seq"], 3, "1qaz98*&fjwla%"),
            (["lower"], ["num_seq"], 2, "ncvkahei&593))12"),
            (["upper"], ["alphabet_seq", "special_seq", "num_seq"], 3, "a@#b12dc*(12&*"),
            (["lower"], ["alphabet_seq", "special_seq", "num_seq", "duplicate_char"], 3, "a@##b1222dc*(12&**"),
            (["lower"], ["alphabet_seq", "special_seq", "num_seq", "duplicate_char"], 3, "a@##BbB12dc*(12&**"),
            (["lower"], ["alphabet_seq", "special_seq", "num_seq", "duplicate_char"], 3, "a@###b122dc*(12&**"),
            (["lower"], ["alphabet_seq", "special_seq", "num_seq", "duplicate_char"], "3", "a@###b122dc*(12&**"),
        ],
    )
    def test_exclude_fail(self, include_elements, exclude_elements, max_length, test_case):

        # 由于指定了 custom_regex，这里的长度和内置验证规则不再生效
        pv = PasswordValidator(
            max_length=20,
            min_length=4,
            include_elements=include_elements,
            exclude_elements_config={e: max_length for e in exclude_elements},
        )
        with pytest.raises(ValidationError):
            pv.validate(test_case)
