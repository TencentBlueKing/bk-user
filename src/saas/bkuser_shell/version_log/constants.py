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
from enum import Enum


class ChoicesEnum(Enum):
    @classmethod
    def get_choices(cls):
        return cls._choices_labels.value

    @classmethod
    def get_choice_label(cls, value):
        if isinstance(value, Enum):
            value = value.value
        return dict(cls.get_choices()).get(value, value)

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def all(cls) -> list:
        # 过滤 _choice_label
        return [x for x in cls._value2member_map_.keys() if not isinstance(x, tuple)]  # type: ignore


VERSION_PATTERN = re.compile(r"^[vV](\d+\.){1,3}(\d+)$")


class VersionDetailTypes(str, ChoicesEnum):
    """
    changeLogs type枚举类
    """

    NEW = "NEW"
    FIX = "FIX"
    OPTIMIZATION = "OPTIMIZATION"

    def __str__(self):
        return self.value


class ProjectTypes(str, ChoicesEnum):
    """
    项目类型
    """

    API = "API"
    SAAS = "SaaS"
    LOGIN = "Login"
    GLOBAL = "__Global__"

    def __str__(self):
        return self.value
