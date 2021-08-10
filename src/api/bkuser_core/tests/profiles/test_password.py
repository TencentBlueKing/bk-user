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
from bkuser_core.profiles.password import PasswordValidator, get_element_by_name
from rest_framework.exceptions import ValidationError


class TestPasswordValidate:
    @pytest.mark.parametrize("case", ["aaa"])
    def test_get_unknown_element(self, case):
        with pytest.raises(ValueError):
            get_element_by_name(case)

    @pytest.mark.parametrize(
        "required_elements,test_case",
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
    def test_pass(self, required_elements, test_case):
        pv = PasswordValidator(max_length=6, min_length=4, required_element_names=required_elements)
        pv.validate(test_case)

    @pytest.mark.parametrize(
        "required_elements,test_case",
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
    def test_not_pass(self, required_elements, test_case):
        pv = PasswordValidator(max_length=12, min_length=8, required_element_names=required_elements)
        with pytest.raises(ValidationError):
            pv.validate(test_case)
