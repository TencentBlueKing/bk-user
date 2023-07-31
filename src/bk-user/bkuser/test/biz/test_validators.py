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
from rest_framework.exceptions import ValidationError

from bkuser.biz.validators import validate_tenant_id

pytestmark = pytest.mark.django_db


class TestValidator:
    @pytest.mark.parametrize(
        "tenant_id",
        [
            "asdf",
            "123",
            "asdf---...___123",
            "12345678912345678912345678912345",
            "asdf123",
            "asdf123--..",
            "1",
            "a",
            "Asds",
            "0Asd-",
        ],
    )
    def test_right_tenant_id(self, tenant_id):
        """
        校验正确的租户ID
        """
        validate_tenant_id(tenant_id)

    @pytest.mark.parametrize(
        "tenant_id",
        [
            "-asdf",
            ".asdf",
            "asdf@asdf",
            "asdf@123",
            "12345678912345678912345678912345a",
            "/asdf",
            "",
        ],
    )
    def test_wrong_tenant_id(self, tenant_id):
        """
        校验错误的租户ID
        """
        with pytest.raises(ValidationError):
            validate_tenant_id(tenant_id)
