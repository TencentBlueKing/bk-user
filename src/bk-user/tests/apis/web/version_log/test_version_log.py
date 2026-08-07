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

import pytest
from bkuser.apis.web.version_log.file_extractor import FILE_NAME, FILE_NAME_EN, _get_change_log_file_name
from django.utils import translation


class TestVersionLog:
    @pytest.mark.parametrize(
        ("language"),
        [
            ("en"),
            ("en-us"),
        ],
    )
    def test_valid_language_code_en(self, language):
        translation.get_language = lambda: language
        assert _get_change_log_file_name() == FILE_NAME_EN

    @pytest.mark.parametrize(
        ("language"),
        [
            ("zh"),
            ("fr"),
            ("zh-cn"),
        ],
    )
    def test_valid_language_code_zh(self, language):
        translation.get_language = lambda: language
        assert _get_change_log_file_name() == FILE_NAME

    def test_extra_language_with_existing_file(self, tmp_path, settings, monkeypatch):
        """存在对应语言的 changelog 文件时，返回该语言版本日志"""
        (tmp_path / "changelog_ja.md").write_text("test", encoding="utf-8")
        settings.VERSION_LOG_FILES_DIR = str(tmp_path)
        monkeypatch.setattr(translation, "get_language", lambda: "ja")
        assert _get_change_log_file_name() == "changelog_ja.md"

    def test_extra_language_without_file_fallback_to_default(self, tmp_path, settings, monkeypatch):
        """无对应语言文件时，回退到中文默认版本日志"""
        settings.VERSION_LOG_FILES_DIR = str(tmp_path)
        monkeypatch.setattr(translation, "get_language", lambda: "ja")
        assert _get_change_log_file_name() == FILE_NAME
