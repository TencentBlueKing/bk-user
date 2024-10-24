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


class CompatibilityApiErrorCodeEnum(str, StructuredEnum):
    """兼容 API 错误码"""

    SUCCESS = EnumField("SUCCESS")
    PARAM_NOT_VALID = EnumField("PARAM_NOT_VALID")
    # Note: 以下是 2.x 版本里有的错误码，但实际可能因为某些不知原因，可能不再使用了，这里先注释
    # USER_NOT_EXISTS = EnumField("USER_NOT_EXISTS")
    # USER_NOT_EXISTS2 = EnumField("USER_NOT_EXISTS2")
    # USER_INFO_UPDATE_FAIL = EnumField("USER_INFO_UPDATE_FAIL")
    # ACCESS_PERMISSION_DENIED = EnumField("ACCESS_PERMISSION_DENIED")


CompatibilityApiErrorCodeMap = {
    "v1": {
        CompatibilityApiErrorCodeEnum.SUCCESS: "00",
        CompatibilityApiErrorCodeEnum.PARAM_NOT_VALID: "1200",
        # CompatibilityApiErrorCodeEnum.USER_NOT_EXISTS: "1201",
        # CompatibilityApiErrorCodeEnum.USER_NOT_EXISTS2: "1300",
        # CompatibilityApiErrorCodeEnum.USER_INFO_UPDATE_FAIL: "1202",
        # CompatibilityApiErrorCodeEnum.ACCESS_PERMISSION_DENIED: "1203",
    },
    "v2": {
        CompatibilityApiErrorCodeEnum.SUCCESS: 0,
        CompatibilityApiErrorCodeEnum.PARAM_NOT_VALID: 1302100,
        # CompatibilityApiErrorCodeEnum.USER_NOT_EXISTS: 1302101,
        # CompatibilityApiErrorCodeEnum.USER_NOT_EXISTS2: 1302103,
        # CompatibilityApiErrorCodeEnum.USER_INFO_UPDATE_FAIL: 1302102,
        # CompatibilityApiErrorCodeEnum.ACCESS_PERMISSION_DENIED: 1302403,
    },
    "v3": {
        CompatibilityApiErrorCodeEnum.SUCCESS: 0,
        CompatibilityApiErrorCodeEnum.PARAM_NOT_VALID: 1302100,
        # CompatibilityApiErrorCodeEnum.USER_NOT_EXISTS: 1302101,
        # CompatibilityApiErrorCodeEnum.USER_NOT_EXISTS2: 1302103,
        # CompatibilityApiErrorCodeEnum.USER_INFO_UPDATE_FAIL: 1302102,
        # CompatibilityApiErrorCodeEnum.ACCESS_PERMISSION_DENIED: 1302403,
    },
}
