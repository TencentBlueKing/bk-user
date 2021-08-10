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
from bkuser_shell.tests.apis.utils import get_api_factory
from bkuser_shell.version_log.views import VersionLogViewSet
from rest_framework.test import APITestCase
from semantic_version import validate


class TestApis(APITestCase):
    def setUp(self):
        self.factory = get_api_factory()
        self.list_view = VersionLogViewSet.as_view({"get": "list"})
        self.retrieve_view = VersionLogViewSet.as_view({"get": "retrieve"})

    def test_version_log_list(self):
        request = self.factory.get("/api/version_logs_list/")
        response = self.list_view(request=request)
        for item in response.data["versions"]:
            assert "version" in item.keys(), "version字段不存在"
            assert validate(item["version"]), "version字段值非法"
            assert "changeLogs" in item.keys(), "changeLogs字段不存在"

    def test_version_log_detail(self):
        request = self.factory.get("/api/version_logs_list/")
        response = self.retrieve_view(request=request, version_number="2.0.0")

        assert response.data["version"] == "2.0.0"
        assert "changeLogs" in response.data.keys(), "changeLogs字段不存在"

    def test_version_log_detail_exception(self):
        request = self.factory.get("/api/version_logs_list/")

        exception_version_numbers = ["v2.0.0", "abcde", "1.x"]

        for exception_version_number in exception_version_numbers:
            response = self.retrieve_view(request=request, version_number=exception_version_number)

            assert not response.data["data"], "请求非法版本号 返回不为空"
