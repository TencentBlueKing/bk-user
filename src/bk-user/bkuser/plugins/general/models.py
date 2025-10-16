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
import re

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel, Field, model_validator

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
    PageSizeEnum,
)
from bkuser.plugins.models import BasePluginConfig
from bkuser.utils.url import urljoin


class QueryParam(BaseModel):
    """查询参数"""

    key: str
    value: str


class ServerConfig(BaseModel):
    """数据服务相关配置"""

    # 服务地址
    server_base_url: str
    # 用户数据 API 路径
    user_api_path: str = Field(pattern=API_URL_PATH_REGEX)
    # 用户数据 API 请求参数
    user_api_query_params: list[QueryParam] = []
    # 部门数据 API 路径
    department_api_path: str = Field(pattern=API_URL_PATH_REGEX)
    # 部门数据 API 请求参数
    department_api_query_params: list[QueryParam] = []
    # 单次分页请求数量
    page_size: PageSizeEnum = PageSizeEnum.SIZE_100
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
    # 蓝鲸网关配置
    # server_base_url = urljoin(settings.BK_API_URL_TMPL.format(api_name=gateway_name), gateway_stage)
    gateway_name: str | None = None
    gateway_stage: str | None = None
    tenant_id: str | None = None


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

    @property
    def server_base_url(self) -> str:
        """获取服务基础 url

        对于蓝鲸网关认证方式，将通过 gateway_name 和 gateway_stage 动态构建 server_base_url
        对于其他认证方式，直接使用 server_config 的 server_base_url
        """

        if self.auth_config.method == AuthMethod.BK_APIGATEWAY:
            return urljoin(
                settings.BK_API_URL_TMPL.format(api_name=self.auth_config.gateway_name),
                self.auth_config.gateway_stage,  # type: ignore
            )
        return self.server_config.server_base_url

    @model_validator(mode="after")
    def validate_configs(self) -> "GeneralDataSourcePluginConfig":
        auth_method = self.auth_config.method

        if auth_method == AuthMethod.BK_APIGATEWAY:
            if not self.auth_config.gateway_name or not self.auth_config.gateway_stage:
                raise ValueError(_("蓝鲸网关认证时，gateway_name 和 gateway_stage 不能为空"))

            return self

        # 非蓝鲸网关认证方式，校验 server_base_url 格式
        if not re.match(BASE_URL_REGEX, self.server_config.server_base_url):
            raise ValueError(_("服务地址格式不正确"))
        return self
