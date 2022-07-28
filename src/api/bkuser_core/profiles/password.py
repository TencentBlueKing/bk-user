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
import itertools
from dataclasses import dataclass
from typing import ClassVar, Dict, Generator, List

import regex
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError


class PasswordElement:
    name: ClassVar[str] = ""
    display_name: ClassVar[str] = ""
    regex_pattern: ClassVar[str] = ""

    @classmethod
    def match(cls, value: str, *args, **kwargs):
        result = regex.match(cls.regex_pattern, value)
        if not result:
            raise ValidationError(_("密码需要包含{}").format(cls.display_name))


class UpperElement(PasswordElement):
    name = "upper"
    display_name = "大写字母"
    regex_pattern = r"(?=.*?[A-Z])"


class LowerElement(PasswordElement):
    name = "lower"
    display_name = "小写字母"
    regex_pattern = r"(?=.*?[a-z])"


class IntElement(PasswordElement):
    name = "int"
    display_name = "数字"
    regex_pattern = r"(?=.*?[0-9])"


class SpecialElement(PasswordElement):
    name = "special"
    display_name = "特殊字符（除空格）"
    regex_pattern = r"(?=.*?[_#?~.,!;@$%^&*-])"


class SeqElement(PasswordElement):
    name: ClassVar[str] = ""
    display_name: ClassVar[str] = ""
    seq_list: List[str]

    @classmethod
    def make_sub_regex_list(cls, max_seq_len: int) -> Generator[str, None, None]:
        """切割出可能存在的所有序列
        max_seq_len=3, abcdefg -> abc, bcd, cde, def, efg
        """
        for t in cls.seq_list:
            for index, char in enumerate(t):
                # 当已经切割到字符串尾部时
                if index + max_seq_len > len(t):
                    continue

                yield t[index : index + max_seq_len]

    @classmethod
    def match(cls, value: str, *args, **kwargs):
        max_seq_len = int(kwargs.get("max_seq_len", 3))
        value = value.lower()
        for sub_regex in cls.make_sub_regex_list(max_seq_len):
            result = regex.findall(regex.compile(regex.escape(sub_regex)), value)
            if result:
                raise ValidationError(_("密码不能包含超过 {} 位的{}: {}").format(max_seq_len, cls.display_name, str(sub_regex)))


class KeyboardSeq(SeqElement):
    """键盘序"""

    name = "keyboard_seq"
    display_name = "键盘序"
    seq_list = ["qwertyuiopasdfghjklzxcvbnm", "1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik,9ol.0p;/-['=]\\"]


class NumSeq(SeqElement):
    """数字序"""

    name = "num_seq"
    display_name = "连续数字序"
    seq_list = ["1234567890"]


class AlphabetSeq(SeqElement):
    """字母序"""

    name = "alphabet_seq"
    display_name = "连续字母序"
    seq_list = ["abcdefghijklmnopqrstuvwxyz"]


class SpecialSeq(SeqElement):
    """特殊字符序"""

    name = "special_seq"
    display_name = "连续特殊字符序"
    seq_list = ["!@#$%^&*()_+"]


class DuplicateChar(PasswordElement):
    """字符重复"""

    name = "duplicate_char"
    display_name = "连续重复字符"

    @classmethod
    def match(cls, value: str, *args, **kwargs):
        max_seq_len = int(kwargs.get("max_seq_len", 3))
        value = value.lower()
        for d in [list(g) for k, g in itertools.groupby(value)]:
            if len(d) >= max_seq_len:
                raise ValidationError(_("密码不能包含超过 {} 位的重复字符: {}").format(max_seq_len, "".join(d)))


_elements = [
    UpperElement,
    LowerElement,
    IntElement,
    SpecialElement,
    KeyboardSeq,
    NumSeq,
    AlphabetSeq,
    SpecialSeq,
    DuplicateChar,
]


def get_element_cls_by_name(name: str):
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
    include_elements: List[str]
    exclude_elements_config: Dict[str, int]

    def validate(self, value: str):
        # 防御，防止存储字符串
        if not int(self.min_length) <= len(value) <= int(self.max_length):
            raise ValidationError(_("密码长度应该在 {} 到 {} 之间").format(self.min_length, self.max_length))

        for e_name in self.include_elements:
            get_element_cls_by_name(e_name).match(value)

        # FIXME: currently the user_settings value type json is not checked before save into database
        # so, we do a protect here, but should fix it in the future, and remove these codes
        if isinstance(self.exclude_elements_config, list) and not self.exclude_elements_config:
            self.exclude_elements_config = {}

        for e_name, max_length in self.exclude_elements_config.items():
            get_element_cls_by_name(e_name).match(value, max_seq_len=max_length)
