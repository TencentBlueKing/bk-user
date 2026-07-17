# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

from bkuser.common.language import get_language_choices, get_language_codes
from django.test.utils import override_settings


class TestGetLanguageChoices:
    def test_only_builtin_when_no_extra(self):
        """未配置额外语言时，仅返回内置语言；英文码为蓝鲸体系的 en（而非 Django 的 en-us）"""
        with override_settings(EXTRA_LANGUAGES=()):
            assert get_language_choices() == [("zh-cn", "中文"), ("en", "英文")]

    def test_append_extra_languages(self):
        """额外语言追加在内置语言之后"""
        with override_settings(EXTRA_LANGUAGES=(("ja", "日本語"), ("ko", "한국어"))):
            assert get_language_choices() == [
                ("zh-cn", "中文"),
                ("en", "英文"),
                ("ja", "日本語"),
                ("ko", "한국어"),
            ]

    def test_extra_does_not_override_builtin(self):
        """额外语言与内置语言重复时，内置语言优先（setdefault 语义）"""
        with override_settings(EXTRA_LANGUAGES=(("zh-cn", "简体中文"), ("en", "English"), ("ja", "日本語"))):
            choices = dict(get_language_choices())
            assert choices["zh-cn"] == "中文"
            assert choices["en"] == "英文"
            assert choices["ja"] == "日本語"


class TestGetLanguageCodes:
    def test_only_builtin_when_no_extra(self):
        with override_settings(EXTRA_LANGUAGES=()):
            assert get_language_codes() == ["zh-cn", "en"]

    def test_with_extra_languages(self):
        with override_settings(EXTRA_LANGUAGES=(("ja", "日本語"),)):
            assert get_language_codes() == ["zh-cn", "en", "ja"]

    def test_codes_consistent_with_choices(self):
        with override_settings(EXTRA_LANGUAGES=(("ja", "日本語"),)):
            assert get_language_codes() == [code for code, _ in get_language_choices()]
