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
from bkuser_core.departments.v3.views import DepartmentViewSet
from bkuser_core.tests.utils import make_simple_department

pytestmark = pytest.mark.django_db


class TestListApis:
    @pytest.fixture(scope="class")
    def view(self):
        return DepartmentViewSet.as_view({"get": "list"})

    # --------------- List ---------------
    def test_department_list(self, factory, view):
        """测试正常用户列表返回"""
        request = factory.get("/api/v3/departments/")
        response = view(request=request)
        data = response.data["results"]
        assert len(data) == 1
        assert data[0]["name"] == "总公司"

    @pytest.mark.parametrize(
        "samples,params,expected",
        [
            (
                {
                    "groupA": {"category_id": 1, "parent_id": None, "id": 10000},
                    "groupB": {"category_id": 2},
                    "groupC": {"category_id": 1, "parent_id": 10000},
                },
                "category_id=1&parent=10000,",
                "groupC",
            ),
            (
                {
                    "groupA": {"category_id": 1, "id": 10000},
                    "groupB": {"category_id": 2},
                    "groupC": {"category_id": 1, "id": 10001, "parent_id": 10000},
                },
                "category_id=1&children=10001,",
                "groupA",
            ),
        ],
    )
    def test_multiple_fields(self, factory, view, samples, params, expected):
        """测试多字段过滤"""
        for k, v in samples.items():
            make_simple_department(k, force_create_params=v)

        url = f"/api/v3/departments/?{params}"
        request = factory.get(url)
        response = view(request=request)

        assert ",".join([r["name"] for r in response.data["results"]]) == expected
