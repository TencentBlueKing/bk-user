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
from rest_framework.test import APIRequestFactory

from bkuser_core.bkiam.views import BaseIAMViewSet, DynamicFieldIAMViewSet

pytestmark = pytest.mark.django_db


class TestIAMFieldsApis:
    """可代替 base 测试"""

    @pytest.fixture
    def factory(self):
        return APIRequestFactory(
            enforce_csrf_checks=False,
            **{
                "Content-Type": "application/json",
                "HTTP_AUTHORIZATION": "iBearer HVp5CNn4th87w5MLT8x1FJw6Rcc5cF3SRT7NlcFILgij",
            },
        )

    @pytest.fixture
    def view(self):
        # 暂时去掉权限中心 basic auth 校验
        BaseIAMViewSet.authentication_classes = []
        BaseIAMViewSet.permission_classes = []

        return DynamicFieldIAMViewSet.as_view({"post": "distribution"})

    # --------------- List Attr ---------------
    def test_list_attr(self, factory, view):
        """测试返回属性列表"""
        body = {"type": "field", "method": "list_attr"}
        request = factory.post("/api/iam/v1/fields/", body)
        response = view(request=request)
        assert response.status_code == 200

    # --------------- List Attr Value ---------------
    def test_list_attr_value(self, factory, view):
        """测试返回属性值列表"""
        DynamicFieldIAMViewSet.available_attr = ["type"]
        body = {
            "type": "field",
            "method": "list_attr_value",
            "filter": {"attr": "type"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)

        # 正常返回调用不到中间件
        assert response.data["count"] == 3
        assert response.status_code == 200

        DynamicFieldIAMViewSet.available_attr = ["name"]
        body = {
            "type": "field",
            "method": "list_attr_value",
            "filter": {"attr": "name"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)
        assert response.data["count"] == 14
        assert response.status_code == 200

    def test_list_keyword_attr_value(self, factory, view):
        """测试位置属性值列表, keyword 过滤"""
        DynamicFieldIAMViewSet.available_attr = ["name"]
        body = {
            "type": "field",
            "method": "list_attr_value",
            "filter": {"attr": "name", "keyword": "username"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)

        assert response.data["count"] == 1
        assert response.status_code == 200

        DynamicFieldIAMViewSet.available_attr = ["name"]
        body = {
            "type": "field",
            "method": "list_attr_value",
            "filter": {"attr": "name", "keyword": "username"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)

        assert response.data["count"] == 1
        assert response.status_code == 200

    def test_list_ids_attr_value(self, factory, view):
        """测试位置属性值列表，ids 过滤"""
        DynamicFieldIAMViewSet.available_attr = ["name"]
        body = {
            "type": "field",
            "method": "list_attr_value",
            "filter": {"attr": "name", "ids": ["username"]},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)

        # 异常返回将被 exception handler 处理
        assert response.data["count"] == 1
        assert response.status_code == 200

        DynamicFieldIAMViewSet.available_attr = ["name"]
        body = {
            "type": "field",
            "method": "list_attr_value",
            "filter": {"attr": "name", "ids": ["usern"]},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)

        # 异常返回将被 exception handler 处理
        assert response.data["count"] == 0
        assert response.status_code == 200

    def test_list_ids_keyword_attr_value(self, factory, view):
        """测试未知属性值列表，ids & keyword 过滤"""
        DynamicFieldIAMViewSet.available_attr = ["name"]
        body = {
            "type": "field",
            "method": "list_attr_value",
            "filter": {"attr": "name", "ids": ["1"], "keyword": "emai"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)

        # 异常返回将被 exception handler 处理
        assert response.data["count"] == 1
        assert response.status_code == 200

        DynamicFieldIAMViewSet.available_attr = ["display_name", "name"]
        body = {
            "type": "field",
            "method": "list_attr_value",
            "filter": {"attr": "display_name", "ids": ["用户名"], "keyword": "emai"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)

        assert response.data["count"] == 1
        assert response.status_code == 200

        DynamicFieldIAMViewSet.available_attr = ["display_name", "name"]
        body = {
            "type": "field",
            "method": "list_attr_value",
            "filter": {"attr": "display_name", "ids": ["用户名"], "keyword": "邮"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)

        assert response.data["count"] == 2
        assert response.status_code == 200

    def test_list_unknown_attr_value(self, factory, view):
        """测试未知属性值列表"""
        DynamicFieldIAMViewSet.available_attr = ["name"]
        body = {
            "type": "field",
            "method": "list_attr_value",
            "filter": {"attr": "xxxxx"},
            "page": {"offset": 0, "limit": 20},
        }
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)

        # 异常返回将被 exception handler 处理
        assert response.data["data"] is None
        assert response.status_code == 200

    def test_offset_limit_page(self, factory, view):
        """测试分页"""
        DynamicFieldIAMViewSet.available_attr = ["name"]
        body = {
            "type": "field",
            "method": "list_attr_value",
            "filter": {"attr": "name"},
            "page": {"offset": 0, "limit": 5},
        }
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)

        assert response.data["count"] == 14
        assert len(response.data["results"]) == 5
        assert response.status_code == 200

        DynamicFieldIAMViewSet.available_attr = ["name"]
        body = {
            "type": "field",
            "method": "list_attr_value",
            "filter": {"attr": "name"},
            "page": {"offset": 2, "limit": 1},
        }
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)

        assert response.data["count"] == 14
        assert len(response.data["results"]) == 1
        assert response.status_code == 200

    # --------------- List Instances ---------------
    def test_list_instances(self, factory, view):
        """测试拉取实例列表"""

        # 不过滤
        DynamicFieldIAMViewSet.available_attr = ["type"]
        body = {"type": "field", "method": "list_instance", "page": {"offset": 0, "limit": 20}}
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)
        assert response.data["count"] == 14

    def test_list_parent_instances(self):
        """测试拉取实例列表, parent 过滤"""

    # --------------- Fetch Instance Info ---------------
    def test_fetch_instance_info_ids(self, factory, view):
        """测试拉取实例列表"""
        body = {"type": "field", "method": "fetch_instance_info", "filter": {"ids": ["1"]}}
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)
        assert len(response.data) == 1

        body = {"type": "field", "method": "fetch_instance_info", "filter": {"ids": ["1", "4", "5"]}}
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)
        assert len(response.data) == 3
        assert response.data

    def test_fetch_instance_info_attrs(self, factory, view):
        """测试拉取实例列表, attrs 选择返回字段"""
        DynamicFieldIAMViewSet.available_attr = ["type", "name", "display_name"]
        body = {
            "type": "field",
            "method": "fetch_instance_info",
            "filter": {"ids": ["1", "3"], "attrs": ["name", "display_name"]},
        }
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)
        assert len(response.data) == 2
        assert response.data[0]["display_name"]
        assert response.data[0]["id"]
        assert not response.data[0].get("type")

    def test_fetch_instance_info_attrs_all(self, factory, view):
        DynamicFieldIAMViewSet.available_attr = ["type", "name"]
        body = {"type": "field", "method": "fetch_instance_info", "filter": {"ids": ["4"]}}
        request = factory.post("/api/iam/v1/fields/", body, format="json")
        response = view(request=request)
        assert len(response.data) == 1
        assert response.data[0]["display_name"]
        assert response.data[0]["id"]
