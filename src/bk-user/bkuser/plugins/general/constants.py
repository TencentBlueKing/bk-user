# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
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
    400: _("请求参数有误，请确保您的路径与参数符合 API 文档的要求"),
    401: _("未授权请求或身份验证失败，请检查您的认证配置并提供正确的认证凭据"),
    403: _("请求被拒绝或没有权限访问，请确保您拥有访问相关资源的权限"),
    404: _("请求的资源未找到，请确保您的路径拼写正确"),
    405: _("请求方法不被允许，请检查您的路径或确保服务支持该请求"),
    429: _("请求过于频繁，请稍后再试"),
    500: _("服务器内部遇到未知错误，请通过日志排查问题原因"),
    501: _("服务器不支持请求的功能，请确保请求的功能已经实现"),
    502: _("服务器作为网关或代理从上游服务器接收到无效响应，请检查上游服务器是否运行正常以及返回的内容是否正确"),
    503: _("服务器暂时过载或维护，当前无法处理请求，请检查服务器资源使用情况并稍后重试"),
    504: _("服务器作为网关或代理，未能及时从上游服务器收到响应，请确保上游服务器是否正常运行"),
}


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
