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
import uuid

import pytest
import re

from bkuser.utils.random import generate_random_str


@pytest.mark.parametrize(
    "length",
    [2, 3, 5, 7, 9, 11],
)
def test_generate_random_str(length):
    random_str = generate_random_str(length)
    result = re.fullmatch(re.compile(r"^[A-Za-z0-9]+$"), random_str)
    assert result
