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
from pydantic import BaseModel, Field

from .constants import AllowedHttpMethodEnum


class DispatchConfigItem(BaseModel):
    action: str = Field(pattern="^[a-zA-Z0-9][a-zA-Z0-9_-]{1,30}[a-zA-Z0-9]$")
    http_method: AllowedHttpMethodEnum
    handler_func_name: str


class TestConnectionResult(BaseModel):
    """连通性测试结果，包含示例数据"""

    ok: bool
    message: str
