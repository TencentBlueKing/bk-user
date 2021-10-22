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
from unittest.mock import patch

import pytest
from bkuser_core.profiles.views import ProfileViewSet
from bkuser_core.tests.apis.utils import get_api_factory
from bkuser_core.tests.utils import make_simple_category, make_simple_dynamic_field, make_simple_profile
from bkuser_core.user_settings.models import Setting

pytestmark = pytest.mark.django_db


class TestListCreateApis:
    @pytest.fixture(scope="class")
    def view(self):
        return ProfileViewSet.as_view({"get": "list", "post": "create"})

    @pytest.fixture(scope="class")
    def obj_view(self):
        return ProfileViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        )

    # --------------- List ---------------
    def test_profile_list(self, factory, view):
        """测试正常用户列表返回"""
        request = factory.get("/api/v2/profiles/")
        response = view(request=request)
        data = response.data["results"]
        assert len(data) == 1
        assert data[0]["username"] == "admin"

    @pytest.mark.parametrize(
        "page_size,all_count,results_count,first_username",
        [
            (1, 3, 1, "admin"),
            (2, 3, 2, "admin"),
            (3, 3, 3, "admin"),
        ],
    )
    def test_profile_page(self, factory, view, page_size, all_count, results_count, first_username):
        """测试正常用户列表返回"""
        # multiple
        make_simple_profile(username="adminAb")
        make_simple_profile(username="adminBa")

        request = factory.get(f"/api/v2/profiles/?page_size={page_size}&page=1&ordering=create_time")
        response = view(request=request)
        assert response.data["count"] == all_count
        assert len(response.data["results"]) == results_count
        assert response.data["results"][0]["username"] == first_username

    @pytest.mark.parametrize("fields", ["username", "username,category_id", "leader,departments"])
    def test_profile_list_fields(self, factory, view, fields):
        """测试正常字段返回"""
        request = factory.get(f"/api/v2/profiles/?fields={fields}")
        response = view(request=request)
        data = response.data["results"]
        assert set(data[0].keys()) == set(fields.split(","))

    @pytest.mark.parametrize(
        "all_count,fields,result_count,include_disabled,expected_fields",
        [
            # 当未传入 include_disabled 并且传入 enabled 字段时
            (10, "id,username,enabled", 5, "false", "id,username,enabled"),
            # 当传入 include_disabled 并且未传入 enabled 字段时
            (10, "id,username", 10, "true", "id,username,enabled"),
            # 当传入 include_disabled 并且传入 enabled 字段时
            (10, "id,username,enabled", 10, "true", "id,username,enabled"),
        ],
    )
    def test_profile_include_enabled_fields(
        self, factory, view, all_count, fields, result_count, include_disabled, expected_fields
    ):
        """测试用户软删除显式拉取和字段选择"""
        for i in range(1, all_count):
            make_simple_profile(f"user{i}", force_create_params={"enabled": i % 2 == 0})
        response = view(request=factory.get(f"/api/v2/profiles/?fields={fields}&include_disabled={include_disabled}"))
        assert response.data["count"] == result_count
        assert set(response.data["results"][0].keys()) == set(expected_fields.split(","))

    @pytest.mark.parametrize("fields", ["xxxxx", "usernam", "department"])
    def test_profile_list_non_fields(self, factory, view, fields):
        """测试未知字段返回"""
        request = factory.get(f"/api/v2/profiles/?fields={fields}")
        response = view(request=request)
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "exact_lookups,lookup_field,target_code,results_count",
        [
            ("ad,admin", "username", 200, 1),
            ("ad", "username", 200, 0),
            ("admin", "id", 400, 0),
            ("default.local", "domain", 200, 1),
            ("1", "id", 200, 1),
        ],
    )
    def test_profile_list_exact_lookups(self, factory, view, exact_lookups, lookup_field, target_code, results_count):
        """测试精确搜索字段返回"""
        # hit
        request = factory.get(f"/api/v2/profiles/?exact_lookups={exact_lookups}&lookup_field={lookup_field}")
        response = view(request=request)
        assert response.status_code == target_code

        if target_code == 200:
            assert len(response.data["results"]) == results_count

    @pytest.mark.parametrize(
        "exact_lookups,target_code,results_count",
        [("adminAb,adminBa", 200, 2), ("adminAb,admina", 200, 1)],
    )
    def test_multiple_profile_list_exact_lookups(self, factory, view, exact_lookups, target_code, results_count):
        # multiple
        make_simple_profile(username="adminAb")
        make_simple_profile(username="adminBa")
        request = factory.get(f"/api/v2/profiles/?exact_lookups={exact_lookups}")
        response = view(request=request)
        assert response.status_code == target_code
        assert len(response.data["results"]) == results_count

    @pytest.mark.parametrize(
        "fuzzy_lookups,lookup_field,target_code,results_count",
        [
            ("ad,admin", "username", 200, 1),
            ("ad", "username", 200, 1),
            ("min", "id", 200, 0),
            ("default", "domain", 200, 1),
            ("1", "id", 200, 1),
        ],
    )
    def test_profile_list_fuzzy_lookups(self, factory, view, fuzzy_lookups, lookup_field, target_code, results_count):
        """测试模糊搜索字段返回"""
        # hit
        request = factory.get(f"/api/v2/profiles/?fuzzy_lookups={fuzzy_lookups}&lookup_field={lookup_field}")
        response = view(request=request)
        assert response.status_code == target_code
        assert len(response.data["results"]) == results_count

    @pytest.mark.parametrize(
        "fuzzy_lookups,target_code,results_count",
        [("Ab,adminBa", 200, 2), ("adminAb,Ba,ab", 200, 2), ("aB,bA", 200, 2)],
    )
    def test_multiple_profile_list_fuzzy_lookups(self, factory, view, fuzzy_lookups, target_code, results_count):
        # multiple
        make_simple_profile(username="adminAb")
        make_simple_profile(username="adminBa")
        request = factory.get(f"/api/v2/profiles/?fuzzy_lookups={fuzzy_lookups}")
        response = view(request=request)
        assert response.status_code == target_code
        assert len(response.data["results"]) == results_count

    @pytest.mark.parametrize(
        "wildcard_search,wildcard_search_fields,target_code,results_count",
        [
            ("lett", "email", 200, 1),
            ("lett", "qq", 200, 0),
            ("345", "qq,email", 200, 1),
            ("xxx", "qq,email", 200, 1),
            ("lett", "", 200, 2),
            ("", "qq,email", 200, 2),
            ("xxx", "qq,xxxx", 400, 0),
        ],
    )
    def test_profile_list_wildcard(
        self,
        factory,
        view,
        wildcard_search,
        wildcard_search_fields,
        target_code,
        results_count,
    ):
        """测试多字段搜索"""
        make_simple_profile(
            username="adminAb",
            force_create_params={"email": "lettest@xxx.com", "qq": "12345"},
        )
        url = "/api/v2/profiles/?"
        if wildcard_search:
            url += f"wildcard_search={wildcard_search}"
        if wildcard_search_fields:
            if wildcard_search:
                url += "&"
            url += f"wildcard_search_fields={wildcard_search_fields}"

        request = factory.get(url)
        response = view(request=request)
        assert response.status_code == target_code
        if target_code == 200:
            assert len(response.data["results"]) == results_count

    @pytest.mark.parametrize(
        "samples,wildcard_search,lookup,expected",
        [
            (
                {"user-a-1": {"category_id": 1}, "user-b-1": {"category_id": 2}, "user-a-2": {"category_id": 1}},
                "wildcard_search=1&wildcard_search_fields=username",
                "exact_lookups=1&lookup_field=category_id",
                "user-a-1",
            ),
            (
                {"user-a-1": {}, "user-b-1": {}, "user-a-2": {}},
                "wildcard_search=a&wildcard_search_fields=username",
                "fuzzy_lookups=user&lookup_field=username",
                "user-a-1,user-a-2",
            ),
            (
                {"user-a-1": {}, "user-b-1": {}, "user-a-2": {}},
                "wildcard_search=a&wildcard_search_fields=username",
                "fuzzy_lookups=2&lookup_field=username",
                "user-a-2",
            ),
        ],
    )
    def test_wildcard_with_lookup(self, factory, view, samples, wildcard_search, lookup, expected):
        """wildcard 和 lookup 查询结合"""
        for k, v in samples.items():
            make_simple_profile(k, force_create_params=v)

        url = f"/api/v2/profiles/?{wildcard_search}&{lookup}"
        request = factory.get(url)
        response = view(request=request)

        assert ",".join([r["username"] for r in response.data["results"]]) == expected

    @pytest.mark.parametrize(
        "factory_params,query_string,target_code,results_count,target_username",
        [
            (
                {"HTTP_RAW_USERNAME": False},
                "?wildcard_search=lette&wildcard_search_fields=domain",
                200,
                1,
                "adminAb@lettest",
            ),
            ({}, "?exact_lookups=admin", 200, 1, "admin"),
        ],
    )
    def test_profile_username_with_domain(
        self,
        factory,
        view,
        factory_params,
        query_string,
        target_code,
        results_count,
        target_username,
    ):
        """测试拉取用户名 domain 逻辑"""
        make_simple_profile(
            username="adminAb",
            force_create_params={"domain": "lettest", "category_id": 2},
        )

        request = get_api_factory(factory_params).get(f"/api/v2/profiles/{query_string}")
        response = view(request=request)
        assert response.status_code == target_code
        assert len(response.data["results"]) == results_count
        assert response.data["results"][0]["username"] == target_username

    @pytest.mark.parametrize(
        "query_string,target_code,results_count,target_username",
        [
            ("?wildcard_search=lette&wildcard_search_fields=domain", 200, 1, "adminAb"),
            ("?exact_lookups=admin", 200, 1, "admin"),
        ],
    )
    def test_profile_username_force_no_domain(
        self, factory, view, query_string, target_code, results_count, target_username
    ):
        """测试拉取用户名 domain 逻辑（强制不带domain）"""
        make_simple_profile(
            username="adminAb",
            force_create_params={"domain": "lettest", "category_id": 2},
        )

        request = factory.get(f"/api/v2/profiles/{query_string}")
        response = view(request=request)
        assert response.status_code == target_code
        assert len(response.data["results"]) == results_count
        assert response.data["results"][0]["username"] == target_username

    @pytest.mark.parametrize(
        "query_string,results_count,target_username",
        [
            ("?ordering=create_time", 2, "admin"),
            ("?ordering=-create_time", 2, "adminAb"),
            ("?ordering=id", 2, "admin"),
            ("?ordering=-id", 2, "adminAb"),
        ],
    )
    def test_profile_list_ordering(self, factory, view, query_string, results_count, target_username):
        """测试列表排序返回"""
        make_simple_profile(
            username="adminAb",
            force_create_params={"domain": "lettest", "category_id": 2},
        )
        request = factory.get(f"/api/v2/profiles/{query_string}")
        response = view(request=request)
        data = response.data["results"]
        assert len(data) == results_count
        assert data[0]["username"] == target_username

    @pytest.mark.parametrize(
        "query_string,target_username_list",
        [
            ("?fuzzy_lookups=admin", ["admin", "adminAb@lettest", "adminBb@lettest"]),
            ("?exact_lookups=adminAb@lettest", ["adminAb@lettest"]),
            ("?exact_lookups=adminBb@lettest", ["adminBb@lettest"]),
            ("?exact_lookups=adminBb@lettest,adminAb@lettest", ["adminAb@lettest", "adminBb@lettest"]),
            ("?exact_lookups=adminBb@let,adminAb@lettest", ["adminAb@lettest"]),
            ("?fuzzy_lookups=adminBb@lett,adminAb@lette", ["adminAb@lettest", "adminBb@lettest"]),
            ("?fuzzy_lookups=admin,adminBb@lett,adminAb@lette", ["admin", "adminAb@lettest", "adminBb@lettest"]),
        ],
    )
    def test_domain_username_lookup(self, factory, view, query_string, target_username_list):
        make_simple_category(domain="lettest", display_name="测试目录")
        make_simple_profile(
            username="adminAb",
            force_create_params={"domain": "lettest", "category_id": 2},
        )
        make_simple_profile(
            username="adminBb",
            force_create_params={"domain": "lettest", "category_id": 2},
        )

        request = get_api_factory({"HTTP_RAW_USERNAME": False}).get(f"/api/v2/profiles/{query_string}")
        response = view(request=request)
        for index, i in enumerate(response.data["results"]):
            assert target_username_list[index] == i["username"]

    @pytest.mark.parametrize(
        "query_string,target_username_list",
        [
            (
                "?fuzzy_lookups=mingli&best_match=1",
                ["mingli", "mingli@lettest", "hmingli@lettest", "minglidddddd@lettest"],
            ),
            (
                "?fuzzy_lookups=mingli&best_match=0",
                ["mingli@lettest", "hmingli@lettest", "minglidddddd@lettest", "mingli"],
            ),
        ],
    )
    def test_domain_username_lookup_best_match(self, factory, view, query_string, target_username_list):
        make_simple_category(domain="lettest", display_name="测试目录")
        make_simple_profile(username="mingli", force_create_params={"domain": "lettest", "category_id": 2})
        make_simple_profile(
            username="hmingli",
            force_create_params={"domain": "lettest", "category_id": 2},
        )
        make_simple_profile(
            username="minglidddddd",
            force_create_params={"domain": "lettest", "category_id": 2},
        )
        make_simple_profile(
            username="mingdddddd",
            force_create_params={"domain": "lettest", "category_id": 2},
        )
        make_simple_profile(
            username="mingli",
            force_create_params={"domain": "default.local", "category_id": 1},
        )

        request = get_api_factory({"HTTP_RAW_USERNAME": False}).get(f"/api/v2/profiles/{query_string}")
        response = view(request=request)
        for index, i in enumerate(response.data["results"]):
            assert target_username_list[index] == i["username"]

    @pytest.mark.parametrize(
        "query_string,target_username_list",
        [
            (
                "?since=2010-10-01T00:00:01.000000",
                ["admin", "bbbbbb"],
            ),
            (
                "?since=2000-10-01T00:00:01.000000",
                ["admin", "aaaaaa", "bbbbbb"],
            ),
            (
                "?until=2000-10-01T00:00:01.000002",
                ["aaaaaa"],
            ),
            (
                "?until=2019-10-01T00:00:01.000000&since=2010-10-01T00:00:01.000000",
                ["bbbbbb"],
            ),
        ],
    )
    def test_profile_since_until(self, view, query_string, target_username_list):
        a = make_simple_profile(
            username="aaaaaa",
        )
        a.create_time = "2000-10-01T00:00:01.000001"
        a.save()

        b = make_simple_profile(
            username="bbbbbb",
        )
        b.create_time = "2010-10-01T00:00:01.000001"
        b.save()

        request = get_api_factory({"HTTP_RAW_USERNAME": False}).get(f"/api/v2/profiles/{query_string}")
        response = view(request=request)

        for index, i in enumerate(response.data["results"]):
            assert target_username_list[index] == i["username"]

    @pytest.mark.parametrize(
        "creating_count, query_string,expected_count",
        [
            (
                10,
                '?exact_lookups=admin")) OR ((enabled="1',
                0,
            ),
            (
                10,
                '?fuzzy_lookups=admin")) OR ((enabled="1',
                0,
            ),
            (
                2,
                "?exact_lookups=admin,testing1",
                2,
            ),
        ],
    )
    def test_profile_sql_inject(self, view, creating_count, query_string, expected_count):
        """测试拉取用户注入风险"""
        for i in range(creating_count):
            make_simple_profile(username=f"testing{i}")

        request = get_api_factory({"HTTP_RAW_USERNAME": False}).get(f"/api/v2/profiles/{query_string}")
        response = view(request=request)

        assert response.data["count"] == expected_count

    @pytest.mark.parametrize(
        "extra_fields,extra_values,expected",
        [
            (
                [
                    ("gender", 1),
                    ("level", "aa"),
                    ("exp", {"11": "xxx"}),
                    ("last", None),
                ],
                {"gender": 0, "level": "vv"},
                {"gender": 0, "level": "vv", "exp": {"11": "xxx"}, "last": None},
            ),
            (
                [("gender", 1), ("level", []), ("exp", {"11": "xxx"}), ("last", None)],
                {"last": "xxx"},
                {"gender": 1, "level": [], "exp": {"11": "xxx"}, "last": "xxx"},
            ),
            (
                [("gender", 1), ("level", []), ("exp", {"11": "xxx"}), ("last", None)],
                [
                    {
                        "is_deleted": False,
                        "name": "\u804c\u7ea7",
                        "is_need": False,
                        "is_import_need": True,
                        "value": "oooo",
                        "is_display": True,
                        "is_editable": True,
                        "is_inner": False,
                        "key": "last",
                        "id": 9,
                        "is_only": False,
                        "type": "string",
                        "order": 9,
                    }
                ],
                {"gender": 1, "level": [], "exp": {"11": "xxx"}, "last": "oooo"},
            ),
            (
                [("gender", 1), ("level", []), ("exp", {"11": "xxx"}), ("last", None)],
                [
                    {
                        "value": "",
                        "key": "last",
                    }
                ],
                {"gender": 1, "level": [], "exp": {"11": "xxx"}, "last": ""},
            ),
        ],
    )
    def test_extras_default_values(self, view, obj_view, extra_fields, extra_values, expected):
        def make_extra_field(extra_field: tuple):
            make_simple_dynamic_field(name=extra_field[0], force_create_params={"default": extra_field[1]})
            return

        for e in extra_fields:
            make_extra_field(e)

            # 测试兼容情况
        if isinstance(extra_values, list):
            with patch("bkuser_core.profiles.models.Profile.custom_validate") as mocked_method:
                mocked_method.return_value = None

                make_simple_profile("test", force_create_params={"extras": extra_values})
        else:
            make_simple_profile("test", force_create_params={"extras": extra_values})

        r1 = obj_view(
            request=get_api_factory().get("/api/v2/profiles/test/?fields=extras"),
            lookup_value="test",
        )
        assert r1.data["extras"] == expected

        r2 = view(request=get_api_factory().get("/api/v2/profiles/?fields=extras"))
        assert r2.data["results"][-1]["extras"] == expected


class TestCreateApis:
    @pytest.fixture
    def factory(self):
        return get_api_factory()

    @pytest.fixture(scope="class")
    def view(self):
        return ProfileViewSet.as_view({"get": "list", "post": "create"})

    # --------------- Create ---------------

    @pytest.mark.parametrize(
        "create_params,expected",
        [
            ({"username": "test1"}, {"username": "test1"}),
            (
                {"username": "test1", "category_id": 1},
                {"username": "test1", "category_id": 1, "domain": "default.local"},
            ),
            (
                # 只认 category_id
                {"username": "test1", "category_id": 1, "domain": "xxxxx"},
                {"username": "test1", "category_id": 1, "domain": "default.local"},
            ),
            (
                {
                    "username": "test1",
                    "category_id": 1,
                    "domain": "xxxxx",
                    "departments": [1],
                },
                {
                    "username": "test1",
                    "category_id": 1,
                    "domain": "default.local",
                    "departments": [{"name": "总公司", "id": 1, "order": 1, "full_name": "总公司"}],
                },
            ),
            (
                {"username": "test1", "country_code": 1},
                {"username": "test1", "country_code": "1", "iso_code": "US"},
            ),
            (
                {"username": "test1"},
                {"username": "test1", "country_code": "86", "iso_code": "CN"},
            ),
            (
                {"username": "test1", "country_code": "86", "iso_code": "US"},
                {"username": "test1", "country_code": "86", "iso_code": "CN"},
            ),
            (
                {"username": "test1", "leader": [1]},
                {
                    "username": "test1",
                    "leader": [{"username": "admin", "id": 1, "display_name": ""}],
                },
            ),
        ],
    )
    def test_profile_create(self, factory, view, create_params, expected: dict):
        """测试用户创建"""
        request = factory.post("/api/v2/profiles/", data=create_params)
        setattr(request, "operator", "faker")

        response = view(request=request)
        for k, v in expected.items():
            assert response.data[k] == v

    def test_profile_create_duplicate(self, factory, view):
        """测试用户异常创建"""
        make_simple_profile(username="test1")

        request = factory.post("/api/v2/profiles/", data={"username": "test1"})
        setattr(request, "operator", "faker")

        response = view(request=request)
        assert response.status_code == 409
        assert response.data["code"] == "USER_ALREADY_EXISTED"

    def test_profile_create_disabled(self, factory, view):
        """测试用户异常创建"""
        p = make_simple_profile(username="test1")
        p.enabled = False
        p.save()

        request = factory.post("/api/v2/profiles/", data={"username": "test1"})
        setattr(request, "operator", "faker")

        response = view(request=request)
        assert response.status_code == 409
        assert response.data["code"] == "USER_ALREADY_EXISTED"

    def test_profile_create_notify(self, factory, view):
        """测试用户异常创建"""
        setting = Setting.objects.get(meta__key="init_password_method", category_id=1)
        setting.value = "random_via_mail"
        setting.save()

        request = factory.post("/api/v2/profiles/", data={"username": "test1"})
        setattr(request, "operator", "faker")

        with patch("bkuser_core.profiles.tasks.send_password_by_email.delay") as mocked_send_mail:
            mocked_send_mail.return_value = None
            _ = view(request=request)
            assert mocked_send_mail.called
