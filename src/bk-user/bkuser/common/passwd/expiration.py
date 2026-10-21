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

from django.utils import timezone

from bkuser.common.constants import PERMANENT_TIME


def get_password_expired_at(valid_days: int) -> datetime.datetime:
    """根据密码有效天数获取密码过期的具体时间"""
    # 有效时间 -1 表示永远有效
    if valid_days < 0:
        return PERMANENT_TIME

    return timezone.now() + datetime.timedelta(days=valid_days)
