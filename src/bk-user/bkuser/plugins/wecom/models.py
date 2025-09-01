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


from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel, Field, model_validator

from bkuser.plugins.models import BasePluginConfig
from bkuser.plugins.wecom.constants import (
    DEFAULT_REQ_TIMEOUT,
    DEFAULT_RETRIES,
    MAX_REQ_TIMEOUT,
    MAX_RETRIES,
    MIN_REQ_TIMEOUT,
    MIN_RETRIES,
    WeComSyncScope,
)


class ServerConfig(BaseModel):
    """服务配置"""

    # 企业微信配置
    corp_id: str
    corp_secret: str
    # 单次请求超时时间
    request_timeout: int = Field(ge=MIN_REQ_TIMEOUT, le=MAX_REQ_TIMEOUT, default=DEFAULT_REQ_TIMEOUT)
    # 请求失败重试次数
    retries: int = Field(ge=MIN_RETRIES, le=MAX_RETRIES, default=DEFAULT_RETRIES)
    # 同步范围
    sync_scope: WeComSyncScope
    # 同步部门 ID （全量同步时，令同步部门 ID 为 0）
    sync_dept_id: int = Field(default=0)

    @model_validator(mode="after")
    def validate_attrs(self) -> "ServerConfig":
        if self.sync_scope == WeComSyncScope.SPECIFIC_DEPT:
            if not self.sync_dept_id:
                raise ValueError(_("指定部门同步时，需要提供部门 ID"))
        # 全量同步时，同步部门 ID 为 0（防御，防止用户误填）
        else:
            self.sync_dept_id = 0
        return self


class WeComDataSourcePluginConfig(BasePluginConfig):
    """企业微信数据源插件配置"""

    sensitive_fields = [
        "server_config.corp_secret",
    ]

    # 服务配置
    server_config: ServerConfig
