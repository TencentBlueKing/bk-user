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
import json
from unittest.mock import patch

import pytest
from requests import Request, Response

from bkuser_core.categories.plugins.custom.client import CustomDataClient
from bkuser_core.categories.plugins.custom.exceptions import CustomAPIRequestFailed
from bkuser_core.categories.plugins.custom.models import CustomTypeList

pytestmark = pytest.mark.django_db


class TestClient:
    @staticmethod
    def make_resp(content: list, status_code: int = 200) -> Response:
        response = Response()
        response._content = str.encode(json.dumps({"count": len(content), "results": content}))  # type: ignore
        response.status_code = status_code

        fake_req = Request(method="GET", json={}, url="")
        fake_req.body = None  # type: ignore

        response.request = fake_req  # type: ignore
        return response

    @pytest.fixture
    def client(self, test_custom_category):
        c = CustomDataClient(
            api_host="test.com",
            category_id=test_custom_category.id,
            paths={"profile": "some-path", "department": "some-path"},
        )
        return c

    @pytest.mark.parametrize(
        "fake_profiles,expected",
        [
            (
                [
                    {
                        "username": "fake-user",
                        "email": "fake@test.com",
                        "code": "code-1",
                        "display_name": "fakeman",
                        "telephone": "13111123445",
                        "leaders": [],
                        "departments": [],
                        "extras": {"aaa": "xxxx", "bbb": "qqqq", "uniquetest": "vvvv"},
                        "position": 0,
                    },
                    {
                        "username": "fake-user-2",
                        "email": "fake2@test.com",
                        "code": "code-2",
                        "display_name": "fakeman2",
                        "telephone": "13111123445",
                        "leaders": ["code-1"],
                        "departments": [],
                        "extras": {"aaa": "xxxx", "bbb": "qqqq", "uniquetest": "vvvv"},
                        "position": 0,
                    },
                ],
                {"code-1", "code-2"},
            ),
        ],
    )
    def test_fetch_profiles(self, client, fake_profiles, expected):

        with patch("requests.get") as mocked_get:
            mocked_get.return_value = self.make_resp(fake_profiles)

            r = client.fetch_profiles()
            assert isinstance(r, CustomTypeList)
            assert len(r.values) == len(fake_profiles)

            assert set(r.items_map.keys()) == expected

    @pytest.mark.parametrize(
        "fake_profiles,expected",
        [
            (
                [
                    {
                        # "code": "code-1",
                        "username": "fake-user",
                        "email": "fake@test.com",
                        "extras": {"aaa": "xxxx", "bbb": "qqqq", "uniquetest": "vvvv"},
                        "position": 0,
                    }
                ],
                TypeError,
            ),
        ],
    )
    def test_fetch_wrong_profiles(self, client, fake_profiles, expected):
        with patch("requests.get") as mocked_get:
            mocked_get.return_value = self.make_resp(fake_profiles)

            with pytest.raises(expected):
                client.fetch_profiles()

    @pytest.mark.parametrize(
        "fake_departments,expected",
        [
            (
                [
                    {"name": "测试部门", "code": "dep1", "parent": None},
                    {"name": "测试部门2", "code": "dep2", "parent": "dep1"},
                ],
                {"dep1", "dep2"},
            ),
        ],
    )
    def test_fetch_departments(self, client, fake_departments, expected):
        with patch("requests.get") as mocked_get:
            mocked_get.return_value = self.make_resp(fake_departments)

            r = client.fetch_departments()
            assert isinstance(r, CustomTypeList)
            assert len(r.values) == len(fake_departments)

            assert set(r.items_map.keys()) == expected

    def test_fetch_exception(self, client):
        with patch("requests.get") as mocked_get:
            mocked_get.return_value = self.make_resp([], 400)

            with pytest.raises(CustomAPIRequestFailed):
                client.fetch_departments()
