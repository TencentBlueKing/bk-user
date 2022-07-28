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

from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.user_settings.loader import ConfigProvider
from bkuser_core.user_settings.models import Setting, SettingMeta

pytestmark = pytest.mark.django_db


class TestConfigLoader:
    @pytest.fixture
    def ldap_category(self):
        return ProfileCategory.objects.create(type=CategoryType.LDAP.value, display_name="Test", domain="test.com")

    @pytest.fixture
    def setting_meta(self, ldap_category):
        return SettingMeta.objects.create(key="test_key", category_type=ldap_category.type)

    def test_config_load(self, ldap_category, setting_meta):
        Setting.objects.create(meta=setting_meta, value="aaaa", category_id=ldap_category.id)
        config_provider = ConfigProvider(ldap_category.id)

        assert config_provider["test_key"] == "aaaa"
