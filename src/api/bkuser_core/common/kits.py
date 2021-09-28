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
import re
from typing import Dict


def convert_camelcase(name: str) -> str:
    """convert CamelCase to snake_case"""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def convert_camelcase_dict(camel_dict: Dict) -> Dict:
    """convert dict key from CamelCase to snake_case"""
    new_dict = {}
    for key, value in camel_dict.items():
        new_dict[convert_camelcase(key)] = value
    return new_dict


def jsonp_2_json(jsonp):
    try:
        l_index = jsonp.index("(") + 1
        r_index = jsonp.rindex(")")
    except ValueError:
        raise ValueError("Input is not in a jsonp format.")

    res = jsonp[l_index:r_index]
    return res
