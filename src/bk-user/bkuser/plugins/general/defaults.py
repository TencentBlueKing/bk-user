# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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

from bkuser.plugins.general.constants import AuthMethod, PageSizeEnum
from bkuser.plugins.general.models import AuthConfig, GeneralDataSourcePluginConfig, ServerConfig

# 通用 HTTP 数据源插件默认配置
DEFAULT_PLUGIN_CONFIG = GeneralDataSourcePluginConfig(
    server_config=ServerConfig(
        server_base_url="https://bk.example.com",
        user_api_path="/api/v1/users",
        department_api_path="/api/v1/departments",
        page_size=PageSizeEnum.SIZE_100,
        request_timeout=30,
        retries=3,
    ),
    auth_config=AuthConfig(
        method=AuthMethod.BASIC_AUTH,
    ),
)
