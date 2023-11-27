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
from enum import Enum
from typing import List
from unittest import mock

import pytest
from bkuser.apps.global_setting.data_models import validate_global_setting_value_type
from pydantic import BaseModel, ValidationError


def _mock_global_setting_value_type_map():
    class TestTypeEnum(str, Enum):
        test1 = "type1"
        test2 = "type2"

    class SubDataModel(BaseModel):
        type: TestTypeEnum
        id: int
        name: str

    class DataModel(BaseModel):
        id: int
        name: str
        ok: bool
        children: List[int]
        subs: List[SubDataModel]

    return {
        "test_bool": bool,
        "test_int": int,
        "test_string": str,
        "test_int_list": List[int],
        "test_data_obj": DataModel,
        "test_data_obj_list": List[DataModel],
    }


@mock.patch(
    "bkuser.apps.global_setting.data_models.global_setting_value_type_map", new=_mock_global_setting_value_type_map()
)
@pytest.mark.parametrize(
    ("global_setting_id", "value", "excepted"),
    [
        # bool
        ("test_bool", True, True),
        ("test_bool", False, False),
        ("test_bool", "137", None),
        ("test_bool", 137, None),
        # int
        ("test_int", 137, 137),
        ("test_int", "x137", None),
        ("test_int", {"value": 137}, None),
        # string
        ("test_string", "yes 137", "yes 137"),
        ("test_string", 137, None),
        # int list
        ("test_int_list", [1, 2, 3], [1, 2, 3]),
        ("test_int_list", ["x1", 2, 3], None),
        # data obj
        (
            "test_data_obj",
            {
                "id": 1,
                "name": "name",
                "ok": True,
                "children": [1, 2, 3],
                "subs": [{"type": "type1", "id": 1, "name": "name"}],
            },
            {
                "id": 1,
                "name": "name",
                "ok": True,
                "children": [1, 2, 3],
                "subs": [{"type": "type1", "id": 1, "name": "name"}],
            },
        ),
        ("test_data_obj", 137, None),
        (
            "test_data_obj",
            {
                "id": 1,
                "name": "name",
                "ok": "xxx",
                "children": [1, 2, 3],
                "subs": [{"type": "type1", "id": 1, "name": "name"}],
            },
            None,
        ),
        (
            "test_data_obj",
            {
                "id": 1,
                "name": "name",
                "ok": True,
                "children": [1, 2, 3],
                "subs": [{"type": "type_error", "id": 1, "name": "name"}],
            },
            None,
        ),
        # data obj list
        (
            "test_data_obj_list",
            [
                {
                    "id": 1,
                    "name": "name",
                    "ok": True,
                    "children": [1, 2, 3],
                    "subs": [{"type": "type1", "id": 1, "name": "name"}],
                }
            ],
            [
                {
                    "id": 1,
                    "name": "name",
                    "ok": True,
                    "children": [1, 2, 3],
                    "subs": [{"type": "type1", "id": 1, "name": "name"}],
                }
            ],
        ),
        ("test_data_obj_list", 137, None),
        (
            "test_data_obj_list",
            [
                {
                    "id": 1,
                    "name": "name",
                    "ok": "xxx",
                    "children": [1, 2, 3],
                    "subs": [{"type": "type1", "id": 1, "name": "name"}],
                }
            ],
            None,
        ),
    ],
)
def test_validate_global_setting_value_type(global_setting_id, value, excepted):
    # 预期值为None, 说明应该有异常
    if excepted is None:
        with pytest.raises(ValidationError):
            validate_global_setting_value_type(global_setting_id, value)
    else:
        # 预期值非None, 说明应该值相等
        assert validate_global_setting_value_type(global_setting_id, value) == excepted
