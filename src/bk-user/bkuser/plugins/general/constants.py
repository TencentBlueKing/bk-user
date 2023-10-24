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
from blue_krill.data_types.enum import EnumField, StructuredEnum

# 服务基础 URL 正则
BASE_URL_REGEX = r"^https?://[a-zA-Z0-9-\.]+(:\d+)?$"

# API 路径正则
API_URL_PATH_REGEX = r"^\/[\w-]+(\/[\w-]+)*\/?$"

# 最小请求超时时间
MIN_REQ_TIMEOUT = 5
# 最大请求超时时间
MAX_REQ_TIMEOUT = 120
# 默认请求超时时间
DEFAULT_REQ_TIMEOUT = 30

# 最小重试次数
MIN_RETRIES = 0
# 最大重试次数
MAX_RETRIES = 3
# 默认重试次数
DEFAULT_RETRIES = 1

# 默认页码
DEFAULT_PAGE = 1
# 获取首条数据用的每页数量
PAGE_SIZE_FOR_FETCH_FIRST = 1
# 最大拉取总数量 100w
MAX_TOTAL_COUNT = 10**6


class AuthMethod(str, StructuredEnum):
    """鉴权方式"""

    BEARER_TOKEN = EnumField("bearer_token", label="BearerToken")
    BASIC_AUTH = EnumField("basic_auth", label="BasicAuth")


class PageSize(int, StructuredEnum):
    """每页数量"""

    CNT_100 = EnumField(100, label="100")
    CNT_200 = EnumField(200, label="200")
    CNT_500 = EnumField(500, label="500")
    CNT_1000 = EnumField(1000, label="1000")
    CNT_2000 = EnumField(2000, label="2000")
    CNT_5000 = EnumField(5000, label="5000")
