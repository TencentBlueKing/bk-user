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

from typing import List

from pydantic import BaseModel, model_validator

from bkuser.utils.passwd.constants import MIN_NOT_CONTINUOUS_COUNT, MIN_PASSWORD_LENGTH


class PasswordRule(BaseModel):
    """密码强度规则"""

    # --- 长度限制类 ---
    # 密码最小长度
    min_length: int
    # 密码最大长度
    max_length: int

    # --- 字符限制类 ---
    # 必须包含小写字母
    contain_lowercase: bool
    # 必须包含大写字母
    contain_uppercase: bool
    # 必须包含数字
    contain_digit: bool
    # 必须包含特殊字符（标点符号）
    contain_punctuation: bool

    # --- 连续性限制类 ---
    # 密码不允许连续 N 位出现
    not_continuous_count: int
    # 不允许键盘序
    not_keyboard_order: bool
    # 不允许连续字母序
    not_continuous_letter: bool
    # 不允许连续数字序
    not_continuous_digit: bool
    # 重复字母，数字，特殊字符
    not_repeated_symbol: bool

    @model_validator(mode="after")
    def validate_attrs(self) -> "PasswordRule":
        """校验密码规则是否合法"""
        if self.min_length < MIN_PASSWORD_LENGTH:
            raise ValueError(f"min_length must be greater than or equal to {MIN_PASSWORD_LENGTH}")

        # 限制的最小长度，大于最大长度，不是合法的规则
        if self.min_length > self.max_length:
            raise ValueError("min_length cannot greater than max_length")

        # 没有选择任意字符集，不是合法的规则
        if not any(
            [
                self.contain_lowercase,
                self.contain_uppercase,
                self.contain_digit,
                self.contain_punctuation,
            ]
        ):
            raise ValueError(
                "at least one of contain_lowercase, contain_uppercase, ",
                "contain_digit, contain_punctuation must be True",
            )

        # 如果设置【密码不允许连续 N 位出现】的限制，则
        if self.not_continuous_count != 0:
            # 1. 该 N 值不允许低于下限，否则会难以生成/设置合法的密码
            if self.not_continuous_count < MIN_NOT_CONTINUOUS_COUNT:
                raise ValueError(f"not_continuous_count cannot less than {MIN_NOT_CONTINUOUS_COUNT} when set")

            # 2. 必须至少包含一个指定的连续性场景
            if not any(
                [
                    self.not_keyboard_order,
                    self.not_continuous_letter,
                    self.not_continuous_digit,
                    self.not_repeated_symbol,
                ]
            ):
                raise ValueError(
                    "at least one of not_keyboard_order, not_continuous_letter, "
                    "not_continuous_digit, not_repeated_symbol must be True"
                )

        return self


class ValidateResult(BaseModel):
    """密码校验结果"""

    # 校验结果
    ok: bool
    # 密码检查的问题，弱通过检查，则为空列表
    details: List[str]

    @property
    def exception_message(self) -> str:
        return ", ".join([str(d) for d in self.details])


class ZxcvbnMatch(BaseModel):
    """zxcvbn 匹配结果"""

    # 匹配到的密码片段
    token: str
    # 片段在原密码的起始位置
    start: int
    # 片段在原密码的结束位置
    end: int

    # 匹配规则：
    # - repeat 重复
    # - date 日期
    # - dictionary 字典
    # - sequence 序列
    # - regex 正则
    # - spatial 空间连续性
    # - bruteforce 暴力破解
    pattern: str

    # 以下为不同的匹配模式的自定义字段，目前仅提取项目需要的

    # ---- 仅 pattern 为 repeat 有值 ----
    # 重复的字符
    base_token: str = ""
    # 相同字符重复次数
    repeat_count: int = 0

    # ---- 仅 pattern 为 dictionary 有值 ----
    # 匹配到的字典名称
    dictionary: str = ""
    # 匹配到的单词
    matched_word: str = ""
    # 是否通过 leet 进行匹配
    l33t: bool = False
    # 是否逆序
    reversed: bool = False

    # ---- 仅 pattern 为 sequence 有值 ----
    # 序列名称，如 lower 小写字母，upper 大写字母，digits 数字 ...
    sequence: str = ""
    # 序列顺序是否为升序
    ascending: bool = False

    # ---- 仅 pattern 为 spatial 有值 ----
    # 匹配到的空间性信息：qwerty 标准键盘序，dvorak 德沃夏克键盘序
    graph: str = ""
    # 空间上序列转向次数（单行为 1）
    turns: int = 0
