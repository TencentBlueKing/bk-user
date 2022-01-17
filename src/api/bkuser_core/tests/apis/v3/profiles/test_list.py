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
from bkuser_core.departments.models import Department
from bkuser_core.profiles.v3.views import ProfileViewSet
from bkuser_core.tests.utils import make_simple_department, make_simple_profile

pytestmark = pytest.mark.django_db


class TestListApis:
    @pytest.fixture(scope="class")
    def view(self):
        return ProfileViewSet.as_view({"get": "list"})

    # --------------- List ---------------
    def test_profile_list(self, factory, view):
        """测试正常用户列表返回"""
        request = factory.get("/api/v3/profiles/")
        response = view(request=request)
        data = response.data["results"]
        assert len(data) == 1
        assert data[0]["username"] == "admin"

    @pytest.mark.parametrize(
        "samples,params,expected",
        [
            (
                {
                    "user-a-1": {"category_id": 1, "telephone": 123456},
                    "user-b-1": {"category_id": 2},
                    "user-a-2": {"category_id": 1},
                },
                "category_id=1&telephone=123456",
                "user-a-1",
            ),
            (
                {
                    "user-a-1": {"qq": "aaaa", "status": "NORMAL"},
                    "user-b-1": {"qq": "aaaa", "status": "DELETED"},
                    "user-a-2": {"qq": "bbbb"},
                },
                "qq=aaaa&status=NORMAL",
                "user-a-1",
            ),
        ],
    )
    def test_multiple_fields(self, factory, view, samples, params, expected):
        """测试多字段过滤"""
        for k, v in samples.items():
            make_simple_profile(k, force_create_params=v)

        url = f"/api/v2/profiles/?{params}"
        request = factory.get(url)
        response = view(request=request)

        assert ",".join([r["username"] for r in response.data["results"]]) == expected

    @pytest.mark.parametrize(
        "samples,query_params,expected",
        [
            (
                {
                    "user-a-1": {"telephone": 123456, "departments": [10001]},
                    "user-b-1": {"departments": [10001, 10002]},
                    "user-a-2": {"departments": [10003]},
                },
                "departments=10001,10002",
                "user-a-1,user-b-1",
            ),
            (
                {
                    "user-a-1": {"telephone": 123456, "departments": [10001]},
                    "user-b-1": {"departments": [10001, 10002]},
                    "user-a-2": {"departments": [10003]},
                },
                "departments=10001,10002&telephone=123456",
                "user-a-1",
            ),
        ],
    )
    def test_m2m_field(self, factory, view, samples, query_params, expected):
        """测试多对多字段过滤"""
        for case in range(0, 5):
            make_simple_department(f"department-{case}", force_create_params={"id": case + 10000})

        for username, params in samples.items():
            departments = params.pop("departments", [])
            p = make_simple_profile(username, force_create_params=params)
            for d in Department.objects.filter(id__in=departments):
                d.add_profile(p)

        url = f"/api/v2/profiles/?{query_params}"
        request = factory.get(url)
        response = view(request=request)
        assert ",".join([r["username"] for r in response.data["results"]]) == expected
