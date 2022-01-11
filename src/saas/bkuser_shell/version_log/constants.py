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

from bkuser_shell.common.constants import ChoicesEnum

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
