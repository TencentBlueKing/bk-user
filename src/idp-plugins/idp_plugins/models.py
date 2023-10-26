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

from pydantic import BaseModel, field_validator

from .constants import ACTION_REGEX, ALLOWED_HTTP_METHODS


class DispatchConfigItem(BaseModel):
    action: str
    http_method: str
    handler_func_name: str

    @field_validator("http_method")
    @classmethod
    def validate_http_method(cls, v: str) -> str:
        if v not in ALLOWED_HTTP_METHODS:
            raise ValueError(f"the http_method of `{v}` not allowed, only support http_method: {ALLOWED_HTTP_METHODS}")
        return v

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if not re.fullmatch(ACTION_REGEX, v):
            raise ValueError(
                "action should 3-32 characters including letters, numbers, underscores (_), and hyphens (-), "
                "and must start with a letter or number"
            )

        return v


class TestConnectionResult(BaseModel):
    """连通性测试结果，包含示例数据"""

    ok: bool
    message: str
