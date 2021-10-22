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
from bkuser_core.departments.views import DepartmentViewSet
from bkuser_core.tests.apis.utils import get_api_factory, make_request_operator_aware
from bkuser_core.tests.utils import (
    attach_pd_relation,
    get_one_object,
    make_simple_category,
    make_simple_department,
    make_simple_dynamic_field,
    make_simple_profile,
)

pytestmark = pytest.mark.django_db


class TestListCreateApis:
    @pytest.fixture(scope="class")
    def view(self):
        return DepartmentViewSet.as_view({"get": "list", "post": "create"})

    @pytest.fixture(scope="class")
    def obj_view(self):
        return DepartmentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        )

    # --------------- List ---------------
    def test_department_list(self, factory, view):
        """测试正常组织列表返回"""
        response = view(request=factory.get("/api/v2/departments/"))

        assert response.data["count"] == 1
        data = response.data["results"]
        assert data[0]["name"] == "总公司"
        assert data[0]["level"] == 0

    @pytest.mark.parametrize(
        "fields,expected",
        [
            (
                "level,name,id",
                {"name": "总公司", "level": 0, "id": 1},
            ),
            (
                "level,id",
                {"level": 0, "id": 1},
            ),
        ],
    )
    def test_department_list_fields(self, factory, view, fields, expected):
        """测试组织列表返回，字段选择"""
        response = view(request=factory.get(f"/api/v2/departments/?fields={fields}"))

        assert response.data["count"] == 1
        data = response.data["results"]
        assert data[0] == expected
        assert len(data[0].keys()) == len(expected.keys())

    @pytest.mark.parametrize(
        "all_count,fields,result_count,include_disabled,expected_fields",
        [
            (10, "id,name,parent,enabled", 5, "false", "id,name,parent,enabled"),
            (10, "id,name,parent", 10, "true", "id,name,parent,enabled"),
            (10, "id,name,parent,enabled", 10, "true", "id,name,parent,enabled"),
        ],
    )
    def test_department_include_enabled_fields(
        self, factory, view, all_count, fields, result_count, include_disabled, expected_fields
    ):
        """测试组织软删除显式拉取和字段选择"""
        parent_id = 1
        for i in range(1, all_count):
            parent_id = make_simple_department(
                f"Dep{i+1}", parent_id=parent_id, force_create_params={"enabled": i % 2 == 0}
            ).id
        response = view(
            request=factory.get(f"/api/v2/departments/?fields={fields}&include_disabled={include_disabled}")
        )
        assert response.data["count"] == result_count
        assert set(response.data["results"][0].keys()) == set(expected_fields.split(","))

    @pytest.mark.parametrize(
        "query_string,expected",
        [
            (
                "?fuzzy_lookups=0,1,2&fields=name,level,id",
                {"name": "总公司", "level": 0, "id": 1},
            ),
            (
                "?fuzzy_lookups=公&lookup_field=name&fields=name,level,id",
                {"name": "总公司", "level": 0, "id": 1},
            ),
        ],
    )
    def test_department_list_fuzzy(self, factory, view, query_string, expected):
        """测试模糊组织列表返回"""
        response = view(request=factory.get(f"/api/v2/departments/{query_string}"))

        assert response.data["count"] == 1
        data = response.data["results"]
        assert data[0] == expected

    @pytest.mark.parametrize(
        "query_string,count,expected",
        [
            (
                "?exact_lookups=0,1,2&fields=name,level,id",
                1,
                {"name": "总公司", "level": 0, "id": 1},
            ),
            ("?exact_lookups=公&lookup_field=name&fields=name,level,id", 0, {}),
            (
                "?exact_lookups=0&lookup_field=level&fields=name,level,id",
                1,
                {"name": "总公司", "level": 0, "id": 1},
            ),
        ],
    )
    def test_department_list_exact(self, factory, view, query_string, count, expected):
        """测试精确组织列表返回"""
        response = view(request=factory.get(f"/api/v2/departments/{query_string}"))

        assert response.data["count"] == count
        data = response.data.get("results", [])
        if data:
            assert data[0] == expected

    @pytest.mark.parametrize(
        "query_string,creating_list,expected",
        [
            (
                "?ordering=level",
                ["部门A"],
                ["总公司", "部门A"],
            ),
            (
                "?ordering=-level",
                ["部门A"],
                ["部门A", "总公司"],
            ),
        ],
    )
    def test_department_list_ordering(self, factory, view, query_string, creating_list, expected):
        """测试组织列表排序"""
        for c in creating_list:
            make_simple_department(name=c, parent_id=1)

        response = view(request=factory.get(f"/api/v2/departments/{query_string}"))
        assert response.data["count"] == len(creating_list) + 1
        assert [r["name"] for r in response.data["results"]] == expected

    @pytest.mark.parametrize(
        "query_string,creating_list,expected",
        [
            (
                "?page_size=2&page=1&ordering=id",
                ["部门A", "部门B"],
                ["总公司", "部门A"],
            ),
            (
                "?page_size=1&page=1&ordering=id",
                ["部门A", "部门B"],
                ["总公司"],
            ),
            (
                "?page_size=3&page=2&ordering=id",
                ["部门A", "部门B", "部门C"],
                ["部门C"],
            ),
        ],
    )
    def test_department_list_page(self, factory, view, query_string, creating_list, expected):
        """测试组织列表分页"""

        for c in creating_list:
            make_simple_department(name=c, parent_id=1)

        response = view(request=factory.get(f"/api/v2/departments/{query_string}"))
        assert response.data["count"] == len(creating_list) + 1
        assert [r["name"] for r in response.data["results"]] == expected

    @pytest.mark.parametrize(
        "query_string,creating_list,expected",
        [
            (
                "?wildcard_search_fields=name&wildcard_search=部门",
                ["部门A", "部门B", "部门C"],
                ["部门A", "部门B", "部门C"],
            ),
            (
                "?wildcard_search_fields=level&wildcard_search=0",
                ["部门A", "部门B"],
                ["总公司"],
            ),
        ],
    )
    def test_department_list_wildcard(self, factory, view, query_string, creating_list, expected):
        """测试组织列表多字段搜索"""
        for c in creating_list:
            make_simple_department(name=c, parent_id=1)

        response = view(request=factory.get(f"/api/v2/departments/{query_string}"))
        assert response.data["count"] == len(expected)
        assert [r["name"] for r in response.data["results"]] == expected

    @pytest.mark.parametrize(
        "query_string,creating_list,expected",
        [
            (
                "/api/v2/departments/?lookup_field=name&exact_lookups=部门B",
                ["部门A", "部门B"],
                "总公司/部门A/部门B",
            ),
            (
                "/api/v2/departments/?lookup_field=name&exact_lookups=部门C",
                ["部门A", "部门B", "部门C"],
                "总公司/部门A/部门B/部门C",
            ),
        ],
    )
    def test_department_list_full_path(self, factory, view, query_string, creating_list, expected):
        """测试组织列表返回的路径字段"""
        parent_id = 1
        for c in creating_list:
            parent_id = make_simple_department(name=c, parent_id=parent_id).id

        response = view(request=factory.get(f"/api/v2/departments/{query_string}"))
        assert response.data["count"] == 1
        assert response.data["results"][0]["full_name"] == expected

    # --------------- Create ---------------
    def test_create_department(self, factory, view):
        """测试创建组织"""
        request = factory.post("/api/v2/departments/", data={"name": "测试部门", "parent": 1, "category_id": 1})
        request = make_request_operator_aware(request, "test")
        response = view(request=request)

        assert Department.objects.all().count() == 2
        assert response.data["name"] == "测试部门"
        assert response.data["full_name"] == "总公司/测试部门"


class TestActionApis:
    @pytest.fixture(scope="class")
    def view(self):
        return DepartmentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
                "post": "restoration",
            }
        )

    # --------------- retrieve ---------------
    def test_department_retrieve(self, factory, view):
        """测试获取组织"""
        # 测试时需要手动指定 kwargs 参数当作路径参数
        response = view(request=factory.get("/api/v2/departments/1/"), lookup_value="1")
        data = response.data
        assert data["name"] == "总公司"

    @pytest.mark.parametrize(
        "lookup_value, creating_list,expected",
        [
            (
                "部门B",
                ["部门A", "部门B", "部门C"],
                "总公司/部门A/部门B",
            ),
            (
                "部门C",
                ["部门A", "部门B", "部门C"],
                "总公司/部门A/部门B/部门C",
            ),
        ],
    )
    def test_department_full_name(self, factory, view, lookup_value, creating_list, expected):
        """测试获取组织全路径名"""
        parent_id = 1
        for c in creating_list:
            parent_id = make_simple_department(name=c, parent_id=parent_id).id

        response = view(
            request=factory.get(f"/api/v2/departments/{lookup_value}?lookup_field=name"),
            lookup_value=lookup_value,
        )
        assert response.data["full_name"] == expected

    @pytest.mark.parametrize(
        "lookup_value, creating_list,expected",
        [
            (
                "部门A",
                ["部门A", "部门B", "部门C"],
                ("部门B", "总公司/部门A/部门B", True),
            ),
            (
                "部门B",
                ["部门A", "部门B", "部门C"],
                ("部门C", "总公司/部门A/部门B/部门C", False),
            ),
        ],
    )
    def test_department_children(self, factory, view, lookup_value, creating_list, expected):
        """测试获取组织的子组织"""
        parent_id = 1
        for c in creating_list:
            parent_id = make_simple_department(name=c, parent_id=parent_id).id

        response = view(
            request=factory.get(f"/api/v2/departments/{lookup_value}?lookup_field=name"),
            lookup_value=lookup_value,
        )
        assert response.data["children"][0]["name"] == expected[0]
        assert response.data["children"][0]["full_name"] == expected[1]
        assert response.data["children"][0]["has_children"] == expected[2]

    def test_department_restoration(self, factory, view):
        d = make_simple_department("foodep", parent_id=1, force_create_params={"enabled": 0})
        request = factory.post(f"/api/v2/departments/{d.id}/restoration/?include_disabled=1")
        setattr(request, "operator", "faker")
        response = view(request=request, lookup_value=f"{d.id}")
        assert response.status_code == 200
        assert get_one_object("department", id=d.id, name=d.name).enabled


class TestGetProfilesApis:
    @pytest.fixture(scope="class")
    def view(self):
        return DepartmentViewSet.as_view({"get": "get_profiles", "post": "add_profiles"})

    @pytest.mark.parametrize(
        "lookup_value, creating_list, raw_username, expected",
        [
            (
                "部门C",
                ["部门A", "部门B", "部门C"],
                False,
                "@test",
            ),
            (
                "部门C",
                ["部门A", "部门B", "部门C"],
                True,
                "user-0",
            ),
        ],
    )
    def test_department_get_profiles_1_cate(self, view, lookup_value, creating_list, raw_username, expected):
        """测试从部门获取人员（当只有一个默认目录时）"""

        parent_id = 1
        for c in creating_list:
            parent_id = make_simple_department(name=c, parent_id=parent_id).id

        target_dep = Department.objects.get(id=parent_id)

        c = make_simple_category("test", display_name="aaaa")
        for i in range(10):
            _fake_p = make_simple_profile(
                username=f"fake-user-{i}",
                force_create_params={"category_id": c.pk, "domain": c.domain},
            )
            attach_pd_relation(profile=_fake_p, department=target_dep)

        _p = make_simple_profile(username="fake-user-default")
        attach_pd_relation(profile=_p, department=target_dep)

        response = view(
            request=get_api_factory({"HTTP_RAW_USERNAME": raw_username}).get(
                f"/api/v2/departments/{lookup_value}/profiles/?lookup_field=name"
            ),
            lookup_value=lookup_value,
        )
        assert len(response.data["results"]) == 11
        assert response.data["results"][0]["username"].endswith(expected)
        assert response.data["results"][-1]["username"] == "fake-user-default"

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
        ],
    )
    def test_department_get_profiles_extras(self, view, extra_fields, extra_values, expected):
        def make_extra_field(extra_field: tuple):
            make_simple_dynamic_field(name=extra_field[0], force_create_params={"default": extra_field[1]})
            return

        for e in extra_fields:
            make_extra_field(e)

        p = make_simple_profile("test", force_create_params={"extras": extra_values})
        d = make_simple_department(parent_id=1, name="xxxx")
        attach_pd_relation(p, d)

        r1 = view(
            request=get_api_factory().get(f"/api/v2/departments/{d.id}/profiles/"),
            lookup_value=d.id,
        )
        assert r1.data["results"][0]["extras"] == expected
