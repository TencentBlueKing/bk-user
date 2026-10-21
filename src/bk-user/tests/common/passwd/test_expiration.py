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
from unittest.mock import patch

from bkuser.common.constants import PERMANENT_TIME
from bkuser.common.passwd import get_password_expired_at
from django.utils import timezone


def test_get_password_expired_at_returns_permanent_time_for_negative_days():
    assert get_password_expired_at(-1) == PERMANENT_TIME


def test_get_password_expired_at_returns_time_after_valid_days():
    now = timezone.now()
    with patch("bkuser.common.passwd.expiration.timezone.now", return_value=now):
        assert get_password_expired_at(90) == now + datetime.timedelta(days=90)
