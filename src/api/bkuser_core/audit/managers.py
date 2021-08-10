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

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from .constants import LogInFailReasonEnum


class ResetPasswordManager(models.Manager):
    """重置密码DB管理器"""


class LogInManager(models.Manager):
    def latest_failed_count(self) -> int:
        """获取上一次成功登陆前最近登陆失败次数"""
        try:
            create_time = self.filter(is_success=True).latest().create_time
            return self.filter(
                is_success=False,
                reason=LogInFailReasonEnum.BAD_PASSWORD.value,  # type: ignore
                create_time__gt=create_time,
            ).count()
        except ObjectDoesNotExist:
            return self.filter(is_success=False, reason=LogInFailReasonEnum.BAD_PASSWORD.value).count()  # type: ignore
