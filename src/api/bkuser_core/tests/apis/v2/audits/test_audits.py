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

from bkuser_core.audit.constants import LogInFailReason, OperationType
from bkuser_core.audit.utils import create_general_log, create_profile_log
from bkuser_core.audit.views import GeneralLogViewSet, LoginLogViewSet, ResetPasswordLogViewSet
from bkuser_core.tests.utils import make_simple_profile

pytestmark = pytest.mark.django_db


class TestGeneralApis:
    @pytest.fixture(scope="class")
    def view(self):
        return GeneralLogViewSet.as_view({"get": "list"})

    @pytest.fixture(scope="class")
    def obj_view(self):
        return GeneralLogViewSet.as_view({"get": "retrieve"})

    # --------------- List ---------------
    @pytest.mark.parametrize(
        "operate_type, username",
        [
            (OperationType.UPDATE.value, "abc"),
            (OperationType.CREATE.value, "edf"),
            (OperationType.DELETE.value, "xyz"),
        ],
    )
    def test_normal_list(self, factory, view, operate_type, username):
        """测试拉取日志返回"""
        operator = "admin"
        operator_obj = make_simple_profile(username=username)
        create_general_log(operator=operator, operator_obj=operator_obj, operate_type=operate_type)

        request = factory.get("/api/v2/general_log/")
        response = view(request=request)
        assert response.data["count"] == 1
        assert response.data["results"][0]["extra_value"]["obj_type"] == "Profile"

    @pytest.mark.parametrize(
        "count, page_size, page, expected",
        [
            (10, 5, 1, 5),
            (4, 5, 1, 4),
            (5, 2, 2, 2),
        ],
    )
    def test_page_size(self, factory, view, count, page_size, page, expected):
        """测试拉取日志返回"""
        operator = "admin"
        operator_obj = make_simple_profile(username="test")
        for _ in range(count):
            create_general_log(
                operator=operator,
                operator_obj=operator_obj,
                operate_type=OperationType.UPDATE.value,
            )

        request = factory.get(f"/api/v2/general_log/?page={page}&page_size={page_size}")
        response = view(request=request)
        assert len(response.data["results"]) == expected


class TestLoginLogApis:
    @pytest.fixture(scope="class")
    def view(self):
        return LoginLogViewSet.as_view({"get": "list"})

    @pytest.fixture(scope="class")
    def obj_view(self):
        return LoginLogViewSet.as_view({"get": "retrieve"})

    @pytest.mark.parametrize(
        "count, page_size, page, expected",
        [
            (10, 5, 1, 5),
            (4, 5, 1, 4),
            (5, 2, 2, 2),
        ],
    )
    def test_profile_log(self, factory, view, count, page_size, page, expected):
        """Test login log fetch with page info"""
        p = make_simple_profile(username="test")
        for _ in range(count):
            create_profile_log(
                profile=p,
                operation="LogIn",
                params={"is_success": False, "reason": LogInFailReason.DISABLED_USER.value},
            )

        request = factory.get(f"/api/v2/login_log/?page={page}&page_size={page_size}")
        response = view(request=request)
        assert len(response.data["results"]) == expected
        assert response.data["results"][0]["reason"] == LogInFailReason.DISABLED_USER.value


class TestResetPasswordApis:
    @pytest.fixture(scope="class")
    def view(self):
        return ResetPasswordLogViewSet.as_view({"get": "list"})

    @pytest.fixture(scope="class")
    def obj_view(self):
        return ResetPasswordLogViewSet.as_view({"get": "retrieve"})

    @pytest.mark.parametrize(
        "count, page_size, page, expected",
        [
            (10, 5, 1, 5),
            (4, 5, 1, 4),
            (5, 2, 2, 2),
        ],
    )
    def test_profile_log(self, factory, view, count, page_size, page, expected):
        """Test login log fetch with page info"""
        p = make_simple_profile(username="test")
        for _ in range(count):
            create_profile_log(
                profile=p,
                operation="ResetPassword",
                params={"is_success": False, "password": "aaaa"},
            )

        request = factory.get(f"/api/v2/reset_password_log/?page={page}&page_size={page_size}")
        response = view(request=request)
        assert len(response.data["results"]) == expected
        assert response.data["results"][0].get("reason") is None
