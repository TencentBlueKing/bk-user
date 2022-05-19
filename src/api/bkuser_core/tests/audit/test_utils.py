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

from bkuser_core.audit.constants import OperationStatus, OperationType
from bkuser_core.audit.models import GeneralLog
from bkuser_core.audit.utils import audit_general_log, create_general_log, create_profile_log
from bkuser_core.common.error_codes import CoreAPIError, error_codes
from bkuser_core.tests import utils

pytestmark = pytest.mark.django_db


class TestUtils:
    @staticmethod
    def make_operator_obj(obj_type_name: str, params: dict):
        return getattr(utils, "make_simple_" + obj_type_name)(**params)

    @pytest.mark.parametrize(
        "operator, operate_type, obj_type, params, expected",
        [
            (
                "zhangsan",
                OperationType.UPDATE.value,
                "profile",
                {"username": "aaa", "force_create_params": {"category_id": 1}},
                {
                    "operation": OperationType.UPDATE.value,
                    "obj_type": "Profile",
                    "display_name": "AAA",
                    "key": "aaa",
                    "category_id": 1,
                },
            ),
            (
                "bbbbb",
                OperationType.CREATE.value,
                "department",
                {
                    "name": "xxxxx",
                    "force_create_params": {"pk": 10000, "category_id": 1},
                },
                {
                    "operation": OperationType.CREATE.value,
                    "obj_type": "Department",
                    "display_name": "xxxxx",
                    "key": 10000,
                    "category_id": 1,
                },
            ),
            (
                "zhangsan",
                OperationType.UPDATE.value,
                "category",
                {
                    "domain": "aaa",
                    "display_name": "qwer",
                    "force_create_params": {"pk": 10000},
                },
                {
                    "operation": OperationType.UPDATE.value,
                    "obj_type": "ProfileCategory",
                    "display_name": "qwer",
                    "category_id": 10000,
                    "key": "aaa",
                },
            ),
            (
                "zhangsan",
                OperationType.CREATE.value,
                "dynamic_field",
                {"name": "aaa", "force_create_params": {"display_name": "qqqq"}},
                {
                    "operation": OperationType.CREATE.value,
                    "obj_type": "DynamicFieldInfo",
                    "display_name": "qqqq",
                    "key": "aaa",
                },
            ),
            (
                "zhangsan",
                OperationType.CREATE.value,
                "dynamic_field",
                {"name": "aaa", "force_create_params": {"display_name": "qqqq"}},
                {
                    "operation": OperationType.CREATE.value,
                    "obj_type": "DynamicFieldInfo",
                    "display_name": "qqqq",
                    "key": "aaa",
                },
            ),
        ],
    )
    def test_create_general_log(self, operator, operate_type, obj_type, params, expected):
        obj = self.make_operator_obj(obj_type, params)
        g = create_general_log(operator, operate_type, obj)

        assert g.operator == operator
        assert g.extra_value == expected

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "operation_type, obj",
        [
            ("None", None),
            (OperationType.CREATE.value, None),
            ("ssss", "zhangsan"),
        ],
    )
    def test_create_general_log_unknown(self, operation_type, obj):
        if obj is not None:
            obj = utils.make_simple_profile(obj)

        assert create_general_log("zhangsan", operation_type, obj) is None

    @pytest.mark.parametrize(
        "operation_type,params",
        [
            ("LogIn", {}),
            ("ResetPassword", {}),
        ],
    )
    def test_create_profile_log(self, operation_type, params):
        assert (
            create_profile_log(utils.make_simple_profile("zhangsan"), operation_type, params=params).__class__.__name__
            == operation_type
        )

    @pytest.mark.parametrize(
        "operation_type,params",
        [
            ("ccc", {}),
            ("uuuu", {}),
        ],
    )
    def test_create_profile_log_error(self, operation_type, params):
        p = utils.make_simple_profile("zhangsan")
        with pytest.raises(ValueError):
            create_profile_log(p, operation_type, params=params)


class TestAuditGeneralLogDeco:
    @pytest.fixture
    def fake_request(self):
        class FakeRequest:
            operator = "fake"
            META = {"HTTP_X_FORWARDED_FOR": "0.0.0.0"}

        return FakeRequest()

    @pytest.fixture
    def dummy_view(self, test_profile):
        class DummyViewSet:
            @audit_general_log(OperationType.UPDATE.value)
            def succeed_view(self, request, **kwargs):
                return "result"

            @audit_general_log(OperationType.RESTORATION.value)
            def failed_view(self, request, **kwargs):
                raise error_codes.CANNOT_CREATE_SETTING.f("fake value error")

            @audit_general_log(OperationType.DELETE.value)
            def unknown_failed_view(self, request, **kwargs):
                raise ValueError("fake value error")

            @audit_general_log(OperationType.UPDATE.value)
            def update_view(self, request, **kwargs):
                test_profile.display_name = "updated"
                return "result"

            def get_object(self):
                return test_profile

        return DummyViewSet()

    def test_success(self, dummy_view, fake_request):
        """test decorator of creating general log"""
        assert dummy_view.succeed_view(fake_request) == "result"

        general_log = GeneralLog.objects.order_by("-create_time").first()
        assert general_log.status == OperationStatus.SUCCEED.value
        assert general_log.extra_value["operation"] == OperationType.UPDATE.value
        assert general_log.extra_value["obj_type"] == "Profile"
        assert general_log.extra_value["key"] == "fake-test"

    def test_unknown_failure(self, dummy_view, fake_request):
        """test decorator of creating general log"""
        with pytest.raises(ValueError):
            assert dummy_view.unknown_failed_view(fake_request) == "result"

        general_log = GeneralLog.objects.order_by("-create_time").first()
        assert general_log.status == OperationStatus.FAILED.value
        assert general_log.extra_value["operation"] == OperationType.DELETE.value
        assert general_log.extra_value["obj_type"] == "Profile"
        assert general_log.extra_value["key"] == "fake-test"
        assert general_log.extra_value["failed_info"] == "未知异常，请查阅日志了解详情"

    def test_failure(self, dummy_view, fake_request):
        """test decorator of creating general log"""
        with pytest.raises(CoreAPIError):
            dummy_view.failed_view(fake_request)

        general_log = GeneralLog.objects.order_by("-create_time").first()
        assert general_log.status == OperationStatus.FAILED.value
        assert general_log.extra_value["operation"] == OperationType.RESTORATION.value
        assert general_log.extra_value["obj_type"] == "Profile"
        assert general_log.extra_value["key"] == "fake-test"
        assert general_log.extra_value["failed_info"] == "无法创建配置, fake value error"

    def test_updated(self, dummy_view, fake_request):
        """test decorator of creating general log"""
        assert dummy_view.update_view(fake_request) == "result"

        general_log = GeneralLog.objects.order_by("-create_time").first()
        assert general_log.status == OperationStatus.SUCCEED.value
        assert general_log.extra_value["operation"] == OperationType.UPDATE.value
        assert general_log.extra_value["obj_type"] == "Profile"
        assert general_log.extra_value["key"] == "fake-test"
        assert general_log.extra_value["display_name"] == "updated"
