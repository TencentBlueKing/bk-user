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
# from unittest import mock

import pytest

from bkuser_core.departments.v2.views import DepartmentViewSet
from bkuser_core.tests.apis.utils import get_api_factory

pytestmark = pytest.mark.django_db


class TestIAMPermissionExtraInfo:
    @pytest.fixture(scope="class")
    def factory(self):
        return get_api_factory(force_params={"HTTP_NEED_IAM": True, "HTTP_ACTION_ID": "manage_department"})

    @pytest.fixture(scope="class")
    def view(self):
        return DepartmentViewSet.as_view({"get": "list", "post": "create"})

    # def test_from_request(self, factory, view):
    #     """测试从 request 生成 info 对象"""
    #     request = factory.get("/api/v2/departments/")
    #     make_request_operator_aware(request, operator="tester")
    #     info = IAMPermissionExtraInfo.from_request(request)

    #     assert info.auth_infos
    #     assert info.auth_infos[0].id == "manage_department"
    #     assert info.auth_infos[0].display_name == IAMAction.get_choice_label(IAMAction.MANAGE_DEPARTMENT)

    # def test_from_request_obj(self, factory, view):
    #     """测试从 request 和 鉴权对象 生成 info 对象"""
    #     request = factory.patch("/api/v2/departments/1/")
    #     make_request_operator_aware(request, operator="tester")
    #     info = IAMPermissionExtraInfo.from_request(request, obj=Department.objects.get(id=1))

    #     assert info.auth_infos
    #     assert info.auth_infos[0].id == "manage_department"
    #     assert info.auth_infos[0].display_name == IAMAction.get_choice_label(IAMAction.MANAGE_DEPARTMENT)
    #     assert info.auth_infos[0].related_resources[0].name == "总公司"
    #     assert info.auth_infos[0].related_resources[0].id == "1"
    #     assert info.auth_infos[0].related_resources[0].type == "department"

    # def test_to_dict(self, factory, view):
    #     """测试从对象生成 dict"""
    #     request = factory.get("/api/v2/departments/")
    #     make_request_operator_aware(request, operator="tester")

    #     def return_fake_callback_url(*arg, **kwargs):
    #         return "http://test.com"

    #     with mock.patch("bkuser_core.bkiam.helper.IAMHelper.generate_callback_url") as mocked_func:
    #         mocked_func.side_effect = return_fake_callback_url
    #         info = IAMPermissionExtraInfo.from_request(request)

    #         raw_info = info.to_dict()

    #         assert raw_info == {
    #             "auth_infos": [
    #                 {
    #                     "display_name": IAMAction.get_choice_label(IAMAction.MANAGE_DEPARTMENT),
    #                     "id": "manage_department",
    #                     "related_resources": [],
    #                 }
    #             ],
    #             "callback_url": return_fake_callback_url(),
    #         }
