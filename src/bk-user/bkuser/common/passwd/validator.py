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
import string
from typing import Dict, List

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from zxcvbn import zxcvbn

from bkuser.common.passwd import PasswordStrengthError
from bkuser.common.passwd.constants import ZxcvbnPattern
from bkuser.common.passwd.models import PasswordRule, ValidateResult, ZxcvbnMatch


class PasswordValidator:
    """密码强度校验器"""

    def __init__(self, rule: PasswordRule):
        self.rule = rule

    def validate(self, password: str, raise_exception=False) -> ValidateResult:
        """根据指定规则，校验密码中存在的问题"""
        ret = ValidateResult(ok=True, errors=[])

        for func in [
            # 密码长度检查
            self._validate_length,
            # 包含的字符检查
            self._validate_contains,
            # 基于 zxcvbn 能力进行检查（弱密码字典/连续性）
            self._validate_with_zxcvbn,
        ]:
            errors = func(password)  # noqa
            if errors:
                ret.ok = False
                ret.errors += errors

        if not ret.ok and raise_exception:
            raise PasswordStrengthError(ret.exception_message)

        return ret

    def _validate_length(self, password: str) -> List[str]:
        """密码长度检查"""
        if len(password) > self.rule.max_length:
            return [_("密码长度至多 {} 位").format(self.rule.max_length)]

        if len(password) < self.rule.min_length:
            return [_("密码长度至少 {} 位").format(self.rule.min_length)]

        return []

    def _validate_contains(self, password: str) -> List[str]:
        """包含的字符检查"""
        contained_chars = set(password)
        errors: List[str] = []

        if set(string.whitespace) & contained_chars:
            errors.append(_("密码不能包含空格或空白符号"))

        if self.rule.contain_lowercase and not (set(string.ascii_lowercase) & contained_chars):
            errors.append(_("密码必须包含小写字母"))

        if self.rule.contain_uppercase and not (set(string.ascii_uppercase) & contained_chars):
            errors.append(_("密码必须包含大写字母"))

        if self.rule.contain_digit and not (set(string.digits) & contained_chars):
            errors.append(_("密码必须包含数字"))

        if self.rule.contain_punctuation and not (set(string.punctuation) & contained_chars):
            errors.append(_("密码必须包含特殊符号"))

        return errors

    def _validate_with_zxcvbn(self, password: str) -> List[str]:
        """基于 zxcvbn 能力进行检查（弱密码字典/连续性）"""

        # NOTE 产品功能上，连续字母序是不区分大小写的，即 abCDef 应当算是连续字母序，
        # 但 zxcvbn 连续字母序匹配是区分大小写的，因此这里使用 password.lower() 进行检查
        zxcvbn_result = zxcvbn(password.lower())
        matches = self._gen_zxcvbn_matches(zxcvbn_result)

        return (
            self._validate_by_zxcvbn_score(zxcvbn_result)
            # 对使用弱密码组合的情况进行限制
            + self._validate_weak_passwd_combination(password, matches)
            # 对键盘序，连续字母，连续数字，连续重复等连续性场景进行检查
            + self._validate_continuous(matches)
        )

    def _gen_zxcvbn_matches(self, zxcvbn_result: Dict) -> List[ZxcvbnMatch]:
        """调用 zxcvbn 获取匹配结果"""
        return [
            ZxcvbnMatch(
                token=m["token"],
                start=m["i"],
                end=m["j"],
                pattern=m["pattern"],
                # repeat
                base_token=m.get("base_token", ""),
                repeat_count=m.get("repeat_count", 0),
                # dictionary
                dictionary=m.get("dictionary", ""),
                matched_word=m.get("matched_word", ""),
                l33t=m.get("l33t", False),
                reversed=m.get("reversed", False),
                # sequence
                sequence=m.get("sequence_name", ""),
                ascending=m.get("ascending", False),
                # spatial
                graph=m.get("graph", ""),
                turns=m.get("turns", 0),
            )
            for m in zxcvbn_result["sequence"]
        ]

    def _validate_by_zxcvbn_score(self, zxcvbn_result: Dict) -> List[str]:
        """根据 zxcvbn 给出的密码评级进行检查"""
        if zxcvbn_result["score"] < settings.MIN_ZXCVBN_PASSWORD_SCORE:
            return [_("密码强度评级过低")]

        return []

    def _validate_weak_passwd_combination(self, password: str, matches: List[ZxcvbnMatch]) -> List[str]:
        """基于 zxcvbn 能力进行检查（弱密码字典）"""
        # 若通过 Leet 映射对部分字符进行替换（如：qw3rt123456）不认为是弱密码词
        matched_words = [m.matched_word for m in matches if m.pattern == ZxcvbnPattern.DICTIONARY and not m.l33t]
        if not matched_words:
            return []

        ratio = len("".join(matched_words)) / len(password)
        # 限制包含的弱密码比例，不可超过预设的阈值
        if ratio > settings.MAX_WEAK_PASSWD_COMBINATION_THRESHOLD:
            return [
                _("密码中包含过多的常见单词或弱密码（如：{} 或 {}）").format(
                    matched_words[0],
                    matched_words[0][::-1],
                )
            ]

        return []

    def _validate_continuous(self, matches: List[ZxcvbnMatch]) -> List[str]:
        """基于 zxcvbn 能力进行检查（连续性）"""
        errors: List[str] = []

        not_continuous_cnt = self.rule.not_continuous_count
        # 没有限制最大连续长度的，提前返回
        if not not_continuous_cnt:
            return errors

        # 标记位，避免同一规则反复触发
        catch_keyboard_order = False
        catch_continuous_letters = False
        catch_continuous_digits = False
        catch_repeated_symbol = False

        for m in matches:
            # 匹配到的密码片段长度小于限制长度，可直接跳过检查
            if len(m.token) < not_continuous_cnt:
                continue

            # 1. 键盘序检查（仅检查标准键盘序 qwerty）
            if (
                self.rule.not_keyboard_order
                and m.pattern == ZxcvbnPattern.SPATIAL
                and m.graph == "qwerty"
                and not catch_keyboard_order
            ):
                errors.append(_("密码不可包含 {} 位键盘序（{}）").format(not_continuous_cnt, m.token))
                catch_keyboard_order = True

            # 2. 连续字母序检查，先前已经将 password 小写化，因此此处仅检查 sequence == lower 即可
            if (
                self.rule.not_continuous_letter
                and m.pattern == ZxcvbnPattern.SEQUENCE
                and m.sequence == "lower"
                and not catch_continuous_letters
            ):
                errors.append(_("密码不可包含 {} 位连续字母序（{}）").format(not_continuous_cnt, m.token))
                catch_continuous_letters = True

            # 3. 连续数字序检查
            if (
                self.rule.not_continuous_digit
                and m.pattern == ZxcvbnPattern.SEQUENCE
                and m.sequence == "digits"
                and not catch_continuous_digits
            ):
                errors.append(_("密码不可包含连续 {} 位数字序（{}）").format(not_continuous_cnt, m.token))
                catch_continuous_digits = True

            # 4. 重复字符检查
            if self.rule.not_repeated_symbol and m.pattern == ZxcvbnPattern.REPEAT and not catch_repeated_symbol:
                errors.append(_("密码不可包含 {} 位重复字符（{}）").format(not_continuous_cnt, m.base_token))
                catch_repeated_symbol = True

        return errors
