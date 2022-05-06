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

from bkuser_core.categories.models import ProfileCategory
from bkuser_core.categories.plugins.local.handlers import make_local_default_settings
from bkuser_core.user_settings.models import Setting

pytestmark = pytest.mark.django_db


class TestHandler:
    @pytest.fixture
    def local_category(self):
        return ProfileCategory.objects.create(domain="fake", display_name="FakeName", type="local")

    @pytest.fixture
    def other_category(self):
        return ProfileCategory.objects.create(domain="fake2", display_name="FakeName2", type="ldap")

    def test_make_local_default_settings(self, local_category, other_category):
        make_local_default_settings(None, local_category)
        assert Setting.objects.filter(category_id=local_category.pk).count()

        make_local_default_settings(None, other_category)
        assert not Setting.objects.filter(category_id=other_category.pk).count()
