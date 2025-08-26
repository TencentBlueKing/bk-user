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

from blue_krill.data_types.enum import EnumField, StructuredEnum

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

# 企业微信API基础URL
WECOM_API_BASE_URL = "https://qyapi.weixin.qq.com/cgi-bin"


class WeComDataType(str, StructuredEnum):
    """企业微信数据类型"""

    DEPARTMENT = EnumField("department", label="部门")
    USER = EnumField("user", label="用户")


class WeComUserStatus(str, StructuredEnum):
    """企业微信用户状态"""

    ACTIVE = EnumField("1", label="已激活")
    DISABLED = EnumField("2", label="已禁用")
    UNACTIVATED = EnumField("4", label="未激活")
    EXITED = EnumField("5", label="退出企业")


class WeComSyncScope(str, StructuredEnum):
    """企业微信同步范围"""

    ALL = EnumField("all", label="全量")
    SPECIFIC_DEPT = EnumField("specific_dept", label="指定部门")
