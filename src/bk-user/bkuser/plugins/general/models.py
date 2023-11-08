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

from bkuser.plugins.general.constants import (
    API_URL_PATH_REGEX,
    BASE_URL_REGEX,
    DEFAULT_REQ_TIMEOUT,
    DEFAULT_RETRIES,
    MAX_REQ_TIMEOUT,
    MAX_RETRIES,
    MIN_REQ_TIMEOUT,
    MIN_RETRIES,
    AuthMethod,
    PageSize,
)
from bkuser.plugins.models import BasePluginConfig


class QueryParam(BaseModel):
    """查询参数"""

    key: str
    value: str


class ServerConfig(BaseModel):
    """数据服务相关配置"""

    # 服务地址
    server_base_url: str = Field(pattern=BASE_URL_REGEX)
    # 用户数据 API 路径
    user_api_path: str = Field(pattern=API_URL_PATH_REGEX)
    # 用户数据 API 请求参数
    user_api_query_params: list[QueryParam] = []
    # 部门数据 API 路径
    department_api_path: str = Field(pattern=API_URL_PATH_REGEX)
    # 部门数据 API 请求参数
    department_api_query_params: list[QueryParam] = []
    # 单次分页请求数量
    page_size: PageSize = PageSize.CNT_100
    # 单次请求超时时间
    request_timeout: int = Field(ge=MIN_REQ_TIMEOUT, le=MAX_REQ_TIMEOUT, default=DEFAULT_REQ_TIMEOUT)
    # 请求失败重试次数
    retries: int = Field(ge=MIN_RETRIES, le=MAX_RETRIES, default=DEFAULT_RETRIES)


class AuthConfig(BaseModel):
    """认证配置"""

    method: AuthMethod
    # bearer token 配置
    bearer_token: str | None = None
    # basic auth 配置
    username: str | None = None
    password: str | None = None


class GeneralDataSourcePluginConfig(BasePluginConfig):
    """通用 HTTP 数据源插件配置"""

    sensitive_fields = [
        "auth_config.bearer_token",
        "auth_config.password",
    ]

    # 服务配置
    server_config: ServerConfig
    # 认证配置
    auth_config: AuthConfig
