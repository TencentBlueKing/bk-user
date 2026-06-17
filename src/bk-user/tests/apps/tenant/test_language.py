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
from bkuser.apps.tenant.language import get_supported_language_codes, update_tenant_user_language
from django.test.utils import override_settings

pytestmark = pytest.mark.django_db


class TestGetSupportedLanguageCodes:
    def test_return_builtin_languages(self):
        assert get_supported_language_codes() == ["zh-cn", "en"]

    def test_return_builtin_and_extra_languages_without_duplicate(self):
        with override_settings(EXTRA_LANGUAGES=[("ja", "日本語"), ("ko", "한국어"), ("en", "English")]):
            assert get_supported_language_codes() == ["zh-cn", "en", "ja", "ko"]


class TestUpdateTenantUserLanguage:
    def test_update_builtin_language(self, not_expired_tenant_user):
        assert update_tenant_user_language(not_expired_tenant_user, "en") is True

        not_expired_tenant_user.refresh_from_db()
        assert not_expired_tenant_user.language == "en"

    def test_update_extra_language(self, not_expired_tenant_user):
        with override_settings(EXTRA_LANGUAGES=[("ja", "日本語")]):
            assert update_tenant_user_language(not_expired_tenant_user, "ja") is True

        not_expired_tenant_user.refresh_from_db()
        assert not_expired_tenant_user.language == "ja"

    def test_skip_update_invalid_language(self, not_expired_tenant_user):
        not_expired_tenant_user.language = "zh-cn"
        not_expired_tenant_user.save(update_fields=["language"])

        assert update_tenant_user_language(not_expired_tenant_user, "zh-US") is False

        not_expired_tenant_user.refresh_from_db()
        assert not_expired_tenant_user.language == "zh-cn"
