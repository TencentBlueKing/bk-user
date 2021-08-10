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
import re
from dataclasses import dataclass
from typing import ClassVar, List, Type

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError


@dataclass
class PasswordElement:
    name: ClassVar[str] = ""
    display_name: ClassVar[str] = ""
    regex_item: ClassVar[str] = ""


class UpperElement(PasswordElement):
    name = "upper"
    display_name = "大写字母"
    regex_item = r"(?=.*?[A-Z])"


class LowerElement(PasswordElement):
    name = "lower"
    display_name = "小写字母"
    regex_item = r"(?=.*?[a-z])"


class IntElement(PasswordElement):
    name = "int"
    display_name = "数字"
    regex_item = r"(?=.*?[0-9])"


class SpecialElement(PasswordElement):
    name = "special"
    display_name = "特殊字符（除空格）"
    regex_item = r"(?=.*?[_#?~.,!;@$%^&*-])"


_elements = [UpperElement, LowerElement, IntElement, SpecialElement]


def get_element_by_name(name: str) -> Type[PasswordElement]:
    """获取密码元素"""
    _map = {x.name: x for x in _elements}
    try:
        return _map[name]
    except KeyError:
        raise ValueError(f"{name} is unknown password element")


@dataclass
class PasswordValidator:
    min_length: int
    max_length: int
    required_element_names: List[str]

    def validate(self, value: str):
        # 防御，防止存储字符串
        if not int(self.min_length) <= len(value) <= int(self.max_length):
            raise ValidationError(_("密码长度应该在 {} 到 {} 之间").format(self.min_length, self.max_length))

        for e_name in self.required_element_names:
            e = get_element_by_name(e_name)
            a = re.match(e.regex_item, value)
            if not a:
                raise ValidationError(_("密码需要包含{}").format(e.display_name))
