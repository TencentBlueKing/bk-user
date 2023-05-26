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

import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.timezone import now

from .constants import LogInFailReason, ResetPasswordFailReason


class ResetPasswordManager(models.Manager):
    """重置密码DB管理器"""

    # pylint: disable=function-name-too-long
    def latest_check_old_password_failed_count(self):
        """最近一段时间重置密码失败的次数，其中最近一段时间指从上一次成功重置密码后到现在"""
        # 查找最近一次成功的时间
        try:
            latest_time = self.filter(is_success=True).latest().create_time
        except ObjectDoesNotExist:
            # 当没有任何成功记录时，防止存在大量失败记录时进行统计导致可能的慢查询，只计算默认配置的统计时间
            # 这里取配置里默认设置的统计时间
            latest_time = now() - datetime.timedelta(seconds=settings.RESET_PASSWORD_RECORD_COUNT_SECONDS)

        return self.filter(
            is_success=False,
            reason=ResetPasswordFailReason.BAD_OLD_PASSWORD.value,
            create_time__gte=latest_time,
        ).count()


class LogInManager(models.Manager):
    def latest_failed_count(self) -> int:
        """获取上一次成功登陆前最近登陆失败次数"""
        # 如果服务运行的时间足够长，单个用户登录记录条目数将会非常多，统计可能会产生慢查询
        # 所以服务维护者可以根据用户登录频次来调整最远统计时间(默认为一个月)
        farthest_count_time = now() - datetime.timedelta(seconds=settings.LOGIN_RECORD_COUNT_SECONDS)
        try:
            latest_success_time = (
                self.filter(is_success=True, create_time__gte=farthest_count_time).latest().create_time
            )
        except ObjectDoesNotExist:
            # 当没有任何成功记录时，直接统计时间区域内的错误次数
            return self.filter(
                is_success=False, reason=LogInFailReason.BAD_PASSWORD.value, create_time__gte=farthest_count_time
            ).count()
        else:
            return self.filter(
                is_success=False,
                reason=LogInFailReason.BAD_PASSWORD.value,
                create_time__gte=latest_success_time,
            ).count()
