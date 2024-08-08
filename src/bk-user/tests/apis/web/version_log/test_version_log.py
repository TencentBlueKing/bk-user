# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

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
