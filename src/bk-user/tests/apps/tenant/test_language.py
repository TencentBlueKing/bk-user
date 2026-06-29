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
from bkuser.apps.tenant.language import (
    get_supported_language_choices,
    get_supported_language_codes,
)
from django.test.utils import override_settings

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _clear_language_cache():
    get_supported_language_choices.cache_clear()
    get_supported_language_codes.cache_clear()
    yield
    get_supported_language_choices.cache_clear()
    get_supported_language_codes.cache_clear()


class TestGetSupportedLanguageCodes:
    def test_return_builtin_languages(self):
        assert get_supported_language_codes() == ["zh-cn", "en"]

    def test_return_extra_languages(self):
        with override_settings(EXTRA_LANGUAGES=[("ja", "日本語")]):
            assert get_supported_language_codes() == ["zh-cn", "en", "ja"]
