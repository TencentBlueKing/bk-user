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

from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _

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

# 服务器返回状态码与错误原因映射
STATUS_CODE_REASON_MAP = {
    400: _("请求参数有误，请检查 API 路径和查询参数是否正确，并确保符合 API 文档的要求"),
    401: _("API 认证失败，请检查认证配置下的认证凭据是否正确"),
    403: _("请求被拒绝，请确保实现的 API 允许用户管理服务调用"),
    404: _("请求的资源未找到，请检查服务地址与 API 路径是否正确"),
    405: _("GET 请求被拒绝，服务地址与 API 路径不正确或 API 未实现 GET 请求，请确保 API 已按照文档实现"),
    429: _("请求过于频繁，请检查实现的 API 是否添加了频率限制，并稍后再试"),
    500: _("实现的 API 服务异常，请查询实现的 API 服务日志排查问题原因"),
    501: _("服务器不支持请求的功能，请确保 API 服务已按照文档实现"),
    502: _("API 未正确响应，请检查实现的 API 服务是否正常或通过日志排查问题原因"),
    503: _("API 无响应或超时，请检查实现的 API 服务是否正常运行"),
    504: _("API 请求未到达，请检查用户管理服务与实现的 API 服务之间网络是否联通，API 服务是否能正确响应"),
}


class AuthMethod(str, StructuredEnum):
    """鉴权方式"""

    BEARER_TOKEN = EnumField("bearer_token", label="BearerToken")
    BASIC_AUTH = EnumField("basic_auth", label="BasicAuth")


class PageSizeEnum(int, StructuredEnum):
    """每页数量"""

    SIZE_100 = EnumField(100, label="100")
    SIZE_200 = EnumField(200, label="200")
    SIZE_500 = EnumField(500, label="500")
    SIZE_1000 = EnumField(1000, label="1000")
    SIZE_2000 = EnumField(2000, label="2000")
    SIZE_5000 = EnumField(5000, label="5000")
