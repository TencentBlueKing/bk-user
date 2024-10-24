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

from blue_krill.data_types.enum import EnumField, StructuredEnum

# 服务 URL 正则
SERVER_URL_REGEX = r"^ldaps?://[a-zA-Z0-9-/\.]+(:\d+)?$"

# LDAP BIND DN 正则：必须提供 1 个 cn/uid，0 或 N 个 ou，0 或 1 个 o，1 或 N 个 dc
LDAP_BIND_DN_REGEX = r"^(cn|uid)=[^,]+(,ou=[^,]+)*(,o=[^,]+)?(,dc=[^,]+)+$"

# LDAP BASE DN 正则：必须提供 0 或 N 个 ou，0 或 1 个 o，1 或 N 个 dc
LDAP_BASE_DN_REGEX = r"^(ou=[^,]+,)*(o=[^,]+,)?(dc=[^,]+,)*(dc=[^,]+)$"

# 最小请求超时时间
MIN_REQ_TIMEOUT = 5
# 最大请求超时时间
MAX_REQ_TIMEOUT = 120
# 默认请求超时时间
DEFAULT_REQ_TIMEOUT = 30

# Operational Attributes 是由 LDAP 服务器管理的特殊属性，
# 用于记录关于条目元数据和其他操作信息，而不是用户定义的实际数据
# 举些例子：
#  - entryUUID：条目的唯一标识符，uuid4
#  - creatorsName：创建条目的用户的 DN，如 cn=admin,dc=example,dc=com
#  - createTimestamp：条目创建的时间戳，如 20230101000000Z
#
# 同步时只会取需要的操作属性 + 所有用户数据属性，避免浪费带宽 & 占用内存
REQUIRED_OPERATIONAL_ATTRIBUTES = ["entryUUID"]


class PageSizeEnum(int, StructuredEnum):
    """每页数量"""

    SIZE_100 = EnumField(100, label="100")
    SIZE_200 = EnumField(200, label="200")
    SIZE_500 = EnumField(500, label="500")
    SIZE_1000 = EnumField(1000, label="1000")
    SIZE_2000 = EnumField(2000, label="2000")
    SIZE_5000 = EnumField(5000, label="5000")
