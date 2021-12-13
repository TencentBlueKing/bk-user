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
from bkuser_core.user_settings.models import Setting, SettingMeta

pytestmark = pytest.mark.django_db


class TestModel:
    def test_make_default_settings(self):
        """测试创建默认配置"""
        local_category = ProfileCategory.objects.create(type="local", domain="test")
        assert Setting.objects.filter(category_id=local_category.id).count() == 0
        local_category.make_default_settings()
        # make sure will not create duplicate setting
        local_category.make_default_settings()
        assert (
            Setting.objects.filter(category_id=local_category.id).count()
            == SettingMeta.objects.filter(category_type=local_category.type).count()
        )
