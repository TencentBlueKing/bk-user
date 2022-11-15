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
from django.conf import settings

from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.categories.plugins.ldap.syncer import LDAPSyncer
from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import Profile
from bkuser_core.tests.apis.utils import get_api_factory
from bkuser_core.tests.categories.plugins.ldap.utils import make_default_settings
from bkuser_core.user_settings.constants import SettingsEnableNamespaces
from bkuser_core.user_settings.loader import ConfigProvider
from bkuser_core.user_settings.models import Setting, SettingMeta

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def reset_cache():
    yield

    # 必须清缓存, locmem放置了一些数据会导致测试互相影响
    from django.core.cache import caches

    caches["locmem"].clear()


@pytest.fixture
def factory():
    return get_api_factory()


@pytest.fixture
def local_category():
    p = ProfileCategory.objects.create(type=CategoryType.LOCAL.value, display_name="Test", domain="test.com")
    # call it manually for lacking celery
    p.make_default_settings()
    return p


@pytest.fixture
def test_ldap_category() -> ProfileCategory:
    p = ProfileCategory.objects.create(type=CategoryType.LDAP.value, display_name="Test", domain="test.com")
    make_default_settings(p)
    return p


@pytest.fixture
def test_ldap_config_provider(test_ldap_category) -> ConfigProvider:
    if not settings.TEST_LDAP:
        return pytest.skip("未配置测试的 Ldap 服务器")

    c = ConfigProvider(test_ldap_category.id)
    c["connection_url"] = settings.TEST_LDAP["url"]
    c["user"] = settings.TEST_LDAP["user"]
    c["password"] = settings.TEST_LDAP["password"]
    c["basic_pull_node"] = settings.TEST_LDAP["base"]
    c["connection_url"] = settings.TEST_LDAP["url"]
    c["user_class"] = settings.TEST_LDAP["user_class"]
    c["organization_class"] = settings.TEST_LDAP["organization_class"]
    c["user"] = settings.TEST_LDAP["user"]
    c["password"] = settings.TEST_LDAP["password"]
    return c


@pytest.fixture
def test_ldap_syncer(test_ldap_category, test_ldap_config_provider) -> LDAPSyncer:
    return LDAPSyncer(category_id=test_ldap_category.id)


@pytest.fixture
def test_profile(test_ldap_category) -> Profile:
    return Profile.objects.create(
        username="fake-test",
        domain=test_ldap_category.domain,
        category_id=test_ldap_category.pk,
    )


@pytest.fixture
def test_department(test_ldap_category) -> Department:
    return Department.objects.create(name="fake-test-dep", category_id=test_ldap_category.pk)


@pytest.fixture
def test_setting_meta() -> SettingMeta:
    return SettingMeta.objects.create(
        namespace=SettingsEnableNamespaces.CONNECTION.value,
        category_type=CategoryType.MAD.value,
        required=True,
        key="test_any_key",
        example="",
    )


@pytest.fixture
def test_setting(test_ldap_category, test_setting_meta) -> Setting:
    return Setting.objects.create(value="aaa", meta=test_setting_meta, category=test_ldap_category)


@pytest.fixture
def test_custom_category():
    p = ProfileCategory.objects.create(type=CategoryType.CUSTOM.value, display_name="Test", domain="test.com")
    p.make_default_settings()
    return p
