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
from bkuser_core.user_settings.models import SettingMeta
from bkuser_core.user_settings.views import SettingViewSet

pytestmark = pytest.mark.django_db


class TestListCreateApis:
    @pytest.fixture(scope="class")
    def view(self):
        return SettingViewSet.as_view({"get": "list", "post": "create"})

    @pytest.fixture(scope="class")
    def obj_view(self):
        return SettingViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        )

    @pytest.fixture(autouse=True)
    def local_category(self):
        p = ProfileCategory.objects.create(domain="fake", display_name="FakeName", type="local")
        p.make_default_settings()
        return p

    # --------------- List ---------------
    def test_category_id_list(self, factory, view, local_category):
        """测试拉取配置列表"""
        request = factory.get(f"/api/v2/settings/?category_id={local_category.pk}")
        response = view(request=request)
        assert len(response.data) == SettingMeta.objects.filter(category_type="local").count()

    def test_wrong_category_id_list(self, factory, view, local_category):
        """测试拉取配置列表，错误 category_id"""
        request = factory.get("/api/v2/settings/?category_id=0")
        response = view(request=request)
        assert response.status_code == 400

    def test_region_wrong_list(self, factory, view, local_category):
        """测试拉取配置列表，错误 region"""
        request = factory.get("/api/v2/settings/?region=xxxx")
        response = view(request=request)
        assert response.status_code == 400

    # --------------- Create ---------------
