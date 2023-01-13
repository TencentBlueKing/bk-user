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
import datetime
import time

import pytest
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now

from bkuser_core.api.login.views import ProfileLoginViewSet
from bkuser_core.categories.constants import CategoryStatus
from bkuser_core.profiles.constants import ProfileStatus, RoleCodeEnum
from bkuser_core.tests.apis.utils import get_api_factory
from bkuser_core.tests.utils import get_one_object, make_simple_category, make_simple_profile
from bkuser_core.user_settings.models import Setting

pytestmark = pytest.mark.django_db


class TestListCreateApis:
    @pytest.fixture(scope="class")
    def factory(self):
        # return get_api_factory({"HTTP_RAW_USERNAME": False})
        return get_api_factory()

    @pytest.fixture(scope="class")
    def check_view(self):
        return ProfileLoginViewSet.as_view({"post": "login"})

    @pytest.fixture(scope="class")
    def query_view(self):
        return ProfileLoginViewSet.as_view({"post": "batch_query"})

    @pytest.fixture(scope="class")
    def upsert_view(self):
        return ProfileLoginViewSet.as_view({"post": "upsert"})

    @property
    def required_return_key(self):
        return [
            "username",
            "email",
            # "telephone",
            # "wx_userid",
            "domain",
            "status",
            # "staff_status",
        ]

    def _assert_required_keys_exist(self, response_data: dict):
        for i in self.required_return_key:
            assert i in response_data

    def test_check(self, factory, check_view):
        """测试登录校验"""
        make_simple_profile(
            username="logintest",
            force_create_params={"password": make_password("testpwd"), "password_update_time": now()},
        )
        request = factory.post("/api/v1/login/check/", data={"username": "logintest", "password": "testpwd"})
        response = check_view(request=request)
        assert response.data
        assert response.data["username"] == "logintest"
        self._assert_required_keys_exist(response.data)

        request = factory.post(
            "/api/v1/login/check/",
            data={"username": "logintest", "password": "testpwd", "domain": "default.local"},
        )
        response = check_view(request=request)
        assert response.data
        assert response.data["username"] == "logintest"
        self._assert_required_keys_exist(response.data)

    def test_other_field_check(self, factory, check_view):
        """测试使用其他字段登录"""
        make_simple_profile(
            username="logintest",
            force_create_params={
                "password": make_password("testpwd"),
                "email": "haha@haha",
                "telephone": "12345",
                "password_update_time": now(),
            },
        )
        request = factory.post("/api/v1/login/check/", data={"username": "logintest", "password": "testpwd"})
        response = check_view(request=request)
        assert response.data
        assert response.data["username"] == "logintest"
        self._assert_required_keys_exist(response.data)

        request = factory.post("/api/v1/login/check/", data={"username": "12345", "password": "testpwd"})
        response = check_view(request=request)
        assert response.data
        assert response.data["username"] == "logintest"
        self._assert_required_keys_exist(response.data)

        request = factory.post("/api/v1/login/check/", data={"username": "haha@haha", "password": "testpwd"})
        response = check_view(request=request)
        assert response.data
        assert response.data["username"] == "logintest"
        self._assert_required_keys_exist(response.data)

    def test_other_field_duplicate(self, factory, check_view):
        """测试使用其他字段登录重复问题"""
        make_simple_profile(
            username="logintest",
            force_create_params={
                "password": make_password("testpwd"),
                "email": "haha@haha",
                "telephone": "12345",
                "password_update_time": now(),
            },
        )
        make_simple_profile(
            username="logintest1",
            force_create_params={
                "password": make_password("testpwd"),
                "email": "haha@haha",
                "telephone": "12345",
                "password_update_time": now(),
            },
        )
        # 实际上是这些字段重复了，但是会模糊错误返回
        request = factory.post("/api/v1/login/check/", data={"username": "12345", "password": "testpwd"})
        response = check_view(request=request)
        assert response.data["code"] == "PASSWORD_ERROR"

        request = factory.post("/api/v1/login/check/", data={"username": "haha@haha", "password": "testpwd"})
        response = check_view(request=request)
        assert response.data["code"] == "PASSWORD_ERROR"

    def test_multiple_domain_check(self, factory, check_view):
        """测试多域登录检验"""
        ca = make_simple_category(domain="testdomain", display_name="测试")
        ca.make_default_settings()
        make_simple_profile(
            username="logintest",
            force_create_params={
                "password": make_password("testpwd"),
                "domain": "testdomain",
                "category_id": ca.id,
                "password_update_time": now(),
            },
        )
        request = factory.post("/api/v1/login/check/", data={"username": "logintest", "password": "testpwd"})
        response = check_view(request=request)

        assert response.data["code"] == "PASSWORD_ERROR"

        # 多域正常
        request = factory.post(
            "/api/v1/login/check/",
            data={"username": "logintest", "password": "testpwd", "domain": "testdomain"},
        )
        response = check_view(request=request)
        assert response.data["username"] == "logintest@testdomain"
        self._assert_required_keys_exist(response.data)

    def test_check_error(self, factory, check_view):
        """测试多域登录失败检验"""
        ca = make_simple_category(domain="testdomain", display_name="测试")
        ca.make_default_settings()
        p = make_simple_profile(
            username="logintest",
            force_create_params={
                "password": make_password("testpwd"),
                "domain": "testdomain",
                "category_id": ca.id,
                "password_update_time": now(),
            },
        )

        # 未知登录域
        request = factory.post(
            "/api/v1/login/check/",
            data={"username": "logintest", "password": "testpwd", "domain": "xxxx"},
        )
        response = check_view(request=request)
        assert response.data["code"] == "DOMAIN_UNKNOWN"

        # 已禁用登录域
        ca.enabled = False
        ca.status = CategoryStatus.INACTIVE.value
        ca.save()
        request = factory.post(
            "/api/v1/login/check/",
            data={"username": "logintest", "password": "testpwd", "domain": "testdomain"},
        )
        response = check_view(request=request)
        assert response.data["code"] == "CATEGORY_NOT_ENABLED"
        ca.enabled = True
        ca.status = CategoryStatus.NORMAL.value
        ca.save()

        # 普通密码错误
        request = factory.post("/api/v1/login/check/", data={"username": "logintest", "password": "testpwd"})
        response = check_view(request=request)
        assert response.data["code"] == "PASSWORD_ERROR"

        # 用户被锁
        p.status = ProfileStatus.LOCKED.value
        p.save()
        request = factory.post(
            "/api/v1/login/check/",
            data={"username": "logintest", "password": "testpwd", "domain": "testdomain"},
        )
        response = check_view(request=request)
        assert response.data["code"] == "PASSWORD_ERROR"

        # 用户被禁用
        p.status = ProfileStatus.DISABLED.value
        p.save()
        request = factory.post(
            "/api/v1/login/check/",
            data={"username": "logintest", "password": "testpwd", "domain": "testdomain"},
        )
        response = check_view(request=request)
        assert response.data["code"] == "PASSWORD_ERROR"

        # 超级用户不对用户状态判断做豁免
        p.role = RoleCodeEnum.SUPERUSER.value
        p.save()
        request = factory.post(
            "/api/v1/login/check/",
            data={"username": "logintest", "password": "testpwd", "domain": "testdomain"},
        )
        response = check_view(request=request)
        assert response.data["code"] == "PASSWORD_ERROR"
        p.role = RoleCodeEnum.STAFF.value
        p.save()

        # 用户密码过期
        p.password_update_time = now() - datetime.timedelta(days=3 * 365)
        p.password_valid_days = 1
        p.status = ProfileStatus.NORMAL.value
        p.save()
        request = factory.post(
            "/api/v1/login/check/",
            data={"username": "logintest", "password": "wrongpwd", "domain": "testdomain"},
        )
        response = check_view(request=request)
        assert response.data["code"] == "PASSWORD_ERROR"

        request = factory.post(
            "/api/v1/login/check/",
            data={"username": "logintest", "password": "testpwd", "domain": "testdomain"},
        )
        response = check_view(request=request)
        assert response.data["code"] == "PASSWORD_EXPIRED"

        # 初始化密码需要修改
        p.password_update_time = None
        p.save()
        request = factory.post(
            "/api/v1/login/check/",
            data={"username": "logintest", "password": "testpwd", "domain": "testdomain"},
        )
        response = check_view(request=request)
        assert response.data["code"] == "SHOULD_CHANGE_INITIAL_PASSWORD"

    def test_check_auto_lock(self, factory, check_view):
        """测试多次错误自动锁定"""
        make_simple_profile(
            username="logintest",
            force_create_params={"password": make_password("testpwd"), "password_update_time": now()},
        )

        auto_unlock_seconds = Setting.objects.get(category__id=1, meta__key="auto_unlock_seconds")
        auto_unlock_seconds.value = 2
        auto_unlock_seconds.save()

        max_trail_times = Setting.objects.get(category__id=1, meta__key="max_trail_times")
        max_trail_times.value = 1
        max_trail_times.save()

        request = factory.post("/api/v1/login/check/", data={"username": "logintest", "password": "wrongpwd"})
        response = check_view(request=request)
        assert response.data["code"] == "PASSWORD_ERROR"

        request = factory.post("/api/v1/login/check/", data={"username": "logintest", "password": "wrongpwd"})
        response = check_view(request=request)
        assert response.data["code"] == "PASSWORD_ERROR"

        # 确保解锁了
        time.sleep(2)
        request = factory.post("/api/v1/login/check/", data={"username": "logintest", "password": "testpwd"})
        response = check_view(request=request)

        self._assert_required_keys_exist(response.data)

        # admin用户不做豁免：
        admin = get_one_object("profile", username="admin")
        admin.set_password("adminpwd")

        request = factory.post("/api/v1/login/check/", data={"username": "admin", "password": "wrongpwd"})
        response = check_view(request=request)
        assert response.data["code"] == "PASSWORD_ERROR"

        request = factory.post("/api/v1/login/check/", data={"username": "admin", "password": "wrongpwd"})
        response = check_view(request=request)
        assert response.data["code"] == "PASSWORD_ERROR"

        # 确保解锁了
        time.sleep(2)
        request = factory.post("/api/v1/login/check/", data={"username": "admin", "password": "adminpwd"})
        response = check_view(request=request)
        self._assert_required_keys_exist(response.data)

    def test_batch_query(self):
        """测试批量查询"""
        # request = self.factory.post('/api/v2/profiles/')

    def test_upsert(self, factory, upsert_view):
        """测试更新插入"""
        body = {"username": "xxx", "domain": "default.local"}
        req = factory.post("/api/v1/login/profile/query/", body)
        resp = upsert_view(request=req)
        assert resp.data["username"] == "xxx"
        assert resp.data["domain"] == "default.local"
        assert resp.data["category_id"] == 1

    def test_upsert_wrong_username(self, factory, upsert_view):
        """测试更新插入"""
        body = {"username": "xxx@xxx", "domain": "default.local"}
        req = factory.post("/api/v1/login/profile/query/", body)
        resp = upsert_view(request=req)
        assert resp.data["code"] == "VALIDATION_ERROR"

    def test_upsert_default_category(self, factory, upsert_view):
        body = {"username": "xxx"}
        req = factory.post("/api/v1/login/profile/query/", body)
        resp = upsert_view(request=req)
        assert resp.data["username"] == "xxx"
        assert resp.data["domain"] == "default.local"
        assert resp.data["category_id"] == 1

    @pytest.mark.parametrize(
        "username, domain, expected",
        [
            ("xxx", "abcd", "DOMAIN_UNKNOWN"),
            ("xxx", "abcd__dd", "VALIDATION_ERROR"),
            ("xxx", "ab@__dd", "VALIDATION_ERROR"),
        ],
    )
    def test_upsert_with_domain(self, factory, upsert_view, username, domain, expected):
        body = {"username": username, "domain": domain}
        req = factory.post("/api/v1/login/profile/query/", body)
        resp = upsert_view(request=req)
        assert resp.data["code"] == expected

    def test_upsert_username_contain_domain(self, factory, upsert_view):
        body = {"username": "xxx@default.local"}
        req = factory.post("/api/v1/login/profile/query/", body)
        resp = upsert_view(request=req)
        assert resp.data["username"] == "xxx"
        assert resp.data["domain"] == "default.local"
