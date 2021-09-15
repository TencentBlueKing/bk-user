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
from bkuser_core.categories.views import CategoryViewSet
from bkuser_core.tests.utils import make_simple_category

pytestmark = pytest.mark.django_db


class TestUpdateApis:
    @pytest.fixture(scope="class")
    def view(self):
        return CategoryViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        )

    def test_update_category(self, view):
        pass


class TestListCreateApis:
    @pytest.fixture(scope="class")
    def view(self):
        return CategoryViewSet.as_view({"get": "list", "post": "create"})

    @pytest.mark.parametrize(
        "all_count,fields,result_count,include_disabled,expected_fields",
        [
            (10, "id,display_name,domain,enabled", 5, "false", "id,display_name,domain,enabled"),
            (10, "id,display_name,domain", 10, "true", "id,display_name,domain,enabled"),
            (10, "id,display_name,domain,enabled", 10, "true", "id,display_name,domain,enabled"),
        ],
    )
    def test_category_include_enabled_fields(
        self, factory, view, all_count, fields, result_count, include_disabled, expected_fields
    ):
        """测试目录软删除显式拉取和字段选择"""
        for i in range(1, all_count):
            make_simple_category(f"domain{i}", f"Display{i}", force_create_params={"enabled": i % 2 == 0})
        response = view(
            request=factory.get(f"/api/v2/categories/?fields={fields}&include_disabled={include_disabled}")
        )
        assert response.data["count"] == result_count
        assert set(response.data["results"][0].keys()) == set(expected_fields.split(","))
