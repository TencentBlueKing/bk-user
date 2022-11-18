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

from bkuser_core.bkiam.converters import PathIgnoreDjangoQSConverter
from bkuser_core.bkiam.permissions import CATEGORY_KEY_MAPPING, DEPARTMENT_KEY_MAPPING


class TestPathIgnoreDjangoQSConverter:
    @pytest.mark.parametrize(
        "policies,expected",
        [
            (
                {
                    "content": [
                        {
                            "content": [
                                {
                                    "field": "department._bk_iam_path_",
                                    "op": "starts_with",
                                    "value": "/category,1/department,3351/",
                                },
                                {
                                    "field": "department._bk_iam_path_",
                                    "op": "starts_with",
                                    "value": "/category,1/department,1/department,3450/",
                                },
                            ],
                            "op": "OR",
                        },
                        {
                            "content": [
                                {"field": "department.id", "op": "eq", "value": "3438"},
                                {
                                    "field": "department._bk_iam_path_",
                                    "op": "starts_with",
                                    "value": "/category,5/department,3440/",
                                },
                            ],
                            "op": "AND",
                        },
                    ],
                    "op": "OR",
                },
                "(OR: ('id', 3351), ('id', 3450), (AND: ('id', '3438'), ('parent_id', 3440)))",
            ),
            (
                {
                    "content": [
                        {
                            "field": "department._bk_iam_path_",
                            "op": "starts_with",
                            "value": "/category,1/department,3351/",
                        },
                        {
                            "field": "department._bk_iam_path_",
                            "op": "starts_with",
                            "value": "/category,1/department,1/department,3450/",
                        },
                    ],
                    "op": "OR",
                },
                "(OR: ('id', 3351), ('id', 3450))",
            ),
            (
                {
                    "field": "department._bk_iam_path_",
                    "op": "starts_with",
                    "value": "/category,1/department,3351/",
                },
                "(AND: ('id', 3351))",
            ),
        ],
    )
    def test_converter(self, policies, expected):
        """测试 filter 转换"""
        # fs = PathIgnoreDjangoQSConverter(ResourceType.get_key_mapping(ResourceType.DEPARTMENT)).convert(policies)
        fs = PathIgnoreDjangoQSConverter(DEPARTMENT_KEY_MAPPING).convert(policies)
        assert str(fs) == expected

    @pytest.mark.parametrize(
        "policies,expected",
        [
            (
                {"field": "category.id", "op": "eq", "value": "1"},
                "(AND: ('id', '1'))",
            ),
        ],
    )
    def test_converter_other(self, policies, expected):
        """测试 filter 转换"""

        # fs = PathIgnoreDjangoQSConverter(ResourceType.get_key_mapping(ResourceType.CATEGORY)).convert(policies)
        fs = PathIgnoreDjangoQSConverter(CATEGORY_KEY_MAPPING).convert(policies)
        assert str(fs) == expected
