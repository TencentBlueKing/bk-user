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

from bkuser_core.bkiam.views import BaseIAMViewSet, DepartmentIAMViewSet
from bkuser_core.tests.apis.utils import get_api_factory
from bkuser_core.tests.utils import make_simple_department

pytestmark = pytest.mark.django_db


class TestIAMDepartmentsApis:
    """可代替 base 测试"""

    @pytest.fixture
    def factory(self):
        return get_api_factory({"HTTP_FORCE_RAW_RESPONSE": False})

    @pytest.fixture
    def view(self):
        # 暂时去掉权限中心 basic auth 校验
        BaseIAMViewSet.authentication_classes = []
        BaseIAMViewSet.permission_classes = []
        return DepartmentIAMViewSet.as_view({"post": "distribution"})

    # --------------- List Attr ---------------
    def test_list_attr(self, factory, view):
        """测试返回属性列表"""
        body = {"type": "department", "method": "list_attr"}
        request = factory.post("/api/iam/v1/departments/", body)
        response = view(request=request)
        assert response.status_code == 200

    # --------------- List Attr Value ---------------
    def test_list_attr_value(self, factory, view):
        """测试返回属性值列表"""
        for i in range(5):
            make_simple_department(name=f"xxx{i}")

        DepartmentIAMViewSet.available_attr = ["id"]
        body = {
            "type": "department",
            "method": "list_attr_value",
            "filter": {"attr": "id"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)

        # 正常返回调用不到中间件
        assert response.data["count"] == 6
        assert response.status_code == 200

        a = make_simple_department(name="parentA")
        b = make_simple_department(name="parentB")

        make_simple_department(name="child", parent_id=a.id)
        make_simple_department(name="child", parent_id=b.id)
        DepartmentIAMViewSet.available_attr = ["name"]
        body = {
            "type": "department",
            "method": "list_attr_value",
            "filter": {"attr": "name"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)
        # 本来应该是10个不同的名字，但是不同父节点是可重名的
        assert response.data["count"] == 9
        assert response.status_code == 200

    def test_list_keyword_attr_value(self, factory, view):
        """测试位置属性值列表, keyword 过滤"""
        DepartmentIAMViewSet.available_attr = ["name"]
        body = {
            "type": "department",
            "method": "list_attr_value",
            "filter": {"attr": "name", "keyword": "总公"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)

        assert response.data["count"] == 1
        assert response.status_code == 200

        DepartmentIAMViewSet.available_attr = ["name"]
        body = {
            "type": "department",
            "method": "list_attr_value",
            "filter": {"attr": "name", "keyword": "总公司"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)

        assert response.data["count"] == 1
        assert response.status_code == 200

        for i in range(5):
            make_simple_department(name=f"xxx{i}")

        body = {
            "type": "department",
            "method": "list_attr_value",
            "filter": {"attr": "name", "keyword": "xxx"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)

        assert response.data["count"] == 5
        assert response.status_code == 200

    def test_list_ids_attr_value(self, factory, view):
        """测试属性值列表，ids 过滤"""
        a = make_simple_department(name="parentA")
        b = make_simple_department(name="parentB")

        make_simple_department(name="child", parent_id=a.id)
        make_simple_department(name="child", parent_id=b.id)

        DepartmentIAMViewSet.available_attr = ["name"]
        body = {
            "type": "department",
            "method": "list_attr_value",
            "filter": {"attr": "name", "ids": ["child", "parentA"]},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)

        # 异常返回将被 exception handler 处理
        assert response.data["count"] == 2
        assert response.status_code == 200

        DepartmentIAMViewSet.available_attr = ["name"]
        body = {
            "type": "department",
            "method": "list_attr_value",
            "filter": {"attr": "name", "ids": ["parentC"]},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)

        # 异常返回将被 exception handler 处理
        assert response.data["count"] == 0
        assert response.status_code == 200

    def test_list_ids_keyword_attr_value(self, factory, view):
        """测试未知属性值列表，ids & keyword 过滤"""
        DepartmentIAMViewSet.available_attr = ["name"]
        body = {
            "type": "department",
            "method": "list_attr_value",
            "filter": {"attr": "name", "ids": ["1"], "keyword": "总公"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)

        # 异常返回将被 exception handler 处理
        assert response.data["count"] == 1
        assert response.status_code == 200

        for i in range(5):
            make_simple_department(name=f"xxx{i}")

        DepartmentIAMViewSet.available_attr = ["name"]
        body = {
            "type": "department",
            "method": "list_attr_value",
            "filter": {"attr": "name", "ids": ["99"], "keyword": "总公司"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)

        # 异常返回将被 exception handler 处理
        assert response.data["count"] == 1
        assert response.status_code == 200

    def test_list_unknown_attr_value(self, factory, view):
        """测试未知属性值列表"""
        DepartmentIAMViewSet.available_attr = ["name"]
        body = {
            "type": "department",
            "method": "list_attr_value",
            "filter": {"attr": "xxxxx"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)

        # 异常返回将被 exception handler 处理
        assert response.data["data"] is None
        assert response.status_code == 200

    def test_offset_limit_page(self, factory, view):
        """测试分页"""
        for i in range(20):
            make_simple_department(name=f"xxx{i}")

        DepartmentIAMViewSet.available_attr = ["name"]
        body = {
            "type": "department",
            "method": "list_attr_value",
            "filter": {"attr": "name"},
            "page": {"offset": 0, "limit": 5},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)

        assert response.data["count"] == 21
        assert len(response.data["results"]) == 5
        assert response.status_code == 200

        DepartmentIAMViewSet.available_attr = ["name"]
        body = {
            "type": "department",
            "method": "list_attr_value",
            "filter": {"attr": "name"},
            "page": {"offset": 6, "limit": 5},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)

        assert response.data["count"] == 21
        assert len(response.data["results"]) == 5
        assert response.status_code == 200

    # --------------- List Instances ---------------
    def test_list_instances(self, factory, view):
        """测试拉取实例列表"""
        body = {"type": "department", "method": "list_instance", "page": {"offset": 0, "limit": 20}}
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)
        assert response.data["count"] == 1

    def test_list_keyword_instances(self, factory, view):
        """测试拉取实例列表, keyword 过滤"""
        body = {
            "type": "department",
            "method": "list_instance",
            "filter": {"keyword": "总"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)

        assert response.data["count"] == 1
        assert [x["display_name"] for x in response.data["results"]] == ["总公司"]

    def test_list_parent_instances(self, factory, view):
        """测试拉取实例列表, parent 过滤"""
        make_simple_department(name="parentA")
        b = make_simple_department(name="parentB")

        make_simple_department(name="child1", parent_id=b.id)
        make_simple_department(name="child2", parent_id=b.id)

        body = {
            "type": "department",
            "method": "list_instance",
            "filter": {"parent": {"id": b.id, "type": "department"}},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)

        assert response.data["count"] == 2
        assert [x["display_name"] for x in response.data["results"]] == ["child1", "child2"]

    # --------------- Fetch Instance Info ---------------
    def test_fetch_instance_info_ids(self, factory, view):
        """测试拉取实例列表"""
        for i in range(5):
            make_simple_department(name=f"xxx{i}", force_create_params={"id": i + 2})

        body = {"type": "department", "method": "fetch_instance_info", "filter": {"ids": ["1"]}}
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)
        assert len(response.data) == 1

        body = {"type": "department", "method": "fetch_instance_info", "filter": {"ids": ["1", "4", "5"]}}
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)
        assert len(response.data) == 3
        assert response.data

    def test_fetch_instance_info_attrs(self, factory, view):
        """测试拉取实例列表, attrs 选择返回字段"""
        DepartmentIAMViewSet.available_attr = ["name", "id"]
        body = {
            "type": "department",
            "method": "fetch_instance_info",
            "filter": {"ids": ["1", "3"], "attrs": ["name", "id"]},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)
        assert len(response.data) == 1
        assert response.data[0]["display_name"]
        assert response.data[0]["id"]

    def test_fetch_instance_info_attrs_all(self, factory, view):
        DepartmentIAMViewSet.available_attr = ["type", "name"]
        body = {"type": "department", "method": "fetch_instance_info", "filter": {"ids": ["1"]}}
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)
        assert len(response.data) == 1
        assert response.data[0]["id"]
        assert response.data[0]["display_name"]

    # --------------- Search Instances ---------------
    def test_search_instances(self, factory, view):
        """测试搜索实例列表"""
        make_simple_department(name="parentA")
        b = make_simple_department(name="parentB")

        make_simple_department(name="child1", parent_id=b.id)
        make_simple_department(name="child2", parent_id=b.id)

        body = {
            "type": "department",
            "method": "search_instance",
            "filter": {"keyword": "rentB"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/departments/", body, format="json")
        response = view(request=request)

        assert response.data["count"] == 1
        assert response.data["results"][0]["child_type"] == "department"
