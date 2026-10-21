# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
import datetime
from hashlib import sha256

from django.utils import timezone

from bkuser.common.constants import PERMANENT_TIME
from bkuser.plugins.local.constants import NEVER_EXPIRE_TIME


def get_password_expired_at(valid_days: int) -> datetime.datetime:
    """根据密码有效天数获取密码过期时间"""
    if valid_days == NEVER_EXPIRE_TIME:
        return PERMANENT_TIME

    return timezone.now() + datetime.timedelta(days=valid_days)


def gen_dept_code(org: str) -> str:
    # 本地数据源数据没有提供部门 code 的方式，
    # 因此使用 sha256 计算以避免冲突，也便于后续插入 DB 时进行比较
    # 注意：本地数据源用户 code 就是 username，不需要额外计算 code
    return sha256(org.encode("utf-8")).hexdigest()
