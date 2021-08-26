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
import math
import random
import string

PROFILES_COUNT = 10000
LEADER_INDEXES = [100, 200, 300, 400]


def make_profile_info(index: int):
    random_num = "".join(random.choice(string.digits) for i in range(8))

    leaders = []
    if index not in LEADER_INDEXES:
        leaders = [f"code-{x}" for x in LEADER_INDEXES]
    return {
        "username": f"fake-user-{index}",
        "email": f"fake-{index}@test.com",
        "code": f"code-{index}",
        "display_name": f"我叫fake{index}",
        "telephone": f"131{random_num}",
        "leaders": leaders,
        "departments": [
            int(math.ceil(index / 10.0)) * 10,
        ],
        "extras": {"aaa": "xxxx", "bbb": "qqqq", "uniquetest": "vvvv"},
        "position": 0,
    }


def serve():
    return {
        "count": PROFILES_COUNT,
        "results": [make_profile_info(index) for index, _ in enumerate(range(PROFILES_COUNT))],
    }
