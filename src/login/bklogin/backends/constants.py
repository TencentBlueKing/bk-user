# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS
Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from enum import Enum


class BkUserCheckCodeEnum(Enum):
    """Bk user check code, defined by api module"""

    # TODO: move into global code
    USER_DOES_NOT_EXIST = 3210010
    TOO_MANY_TRY = 3210011
    USERNAME_FORMAT_ERROR = 3210012
    PASSWORD_ERROR = 3210013
    USER_EXIST_MANY = 3210014
    USER_IS_LOCKED = 3210015
    USER_IS_DISABLED = 3210016
    DOMAIN_UNKNOWN = 3210017
    PASSWORD_EXPIRED = 3210018
    CATEGORY_NOT_ENABLED = 3210019
    ERROR_FORMAT = 3210020
    SHOULD_CHANGE_INITIAL_PASSWORD = 3210021
    USER_IS_EXPIRED = 3210024
