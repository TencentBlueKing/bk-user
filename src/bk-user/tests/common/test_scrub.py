# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
import pytest
from bkuser.common.scrub import scrub_data


@pytest.mark.parametrize(
    ("input", "output"),
    [
        # Data remain intact
        ({"obj": {"value": 3}}, {"obj": {"value": 3}}),
        ("obj=foobar", "obj=foobar"),
        # Case-insensitive
        ({"Password": "bar"}, {"Password": "******"}),
        # Sensitive data at top level
        ({"name": "foo", "bk_token": "bar"}, {"name": "foo", "bk_token": "******"}),
        # Sensitive data at inside level
        (
            {"nested": {"l2": {"name": "foo", "bk_token": "bar"}}, "l1": 0},
            {"nested": {"l2": {"name": "foo", "bk_token": "******"}}, "l1": 0},
        ),
    ],
)
def test_scrub_data(input, output):
    assert scrub_data(input) == output
