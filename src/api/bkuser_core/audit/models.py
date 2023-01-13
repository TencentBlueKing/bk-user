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
import uuid
from dataclasses import dataclass
from typing import Optional

from django.db import models
from jsonfield import JSONField

from bkuser_core.audit.constants import LogInFailReason, OperationStatus, ResetPasswordFailReason
from bkuser_core.audit.managers import LogInManager, ResetPasswordManager
from bkuser_core.common.fields import EncryptField
from bkuser_core.common.models import TimestampedModel


@dataclass
class AuditObjMetaInfo:
    """用于屏蔽不同 model 字段"""

    key: str
    display_name: str
    category_id: Optional[int] = None

    def to_dict(self):
        meta_info = {"key": self.key, "display_name": self.display_name}

        if self.category_id:
            meta_info.update({"category_id": self.category_id})

        return meta_info


class Log(TimestampedModel):
    """操作日志基类"""

    # 很多操作并不会来自 Profile, 所以使用 CharField 更自由灵活
    operator = models.CharField("操作者", null=True, blank=True, max_length=32)
    extra_value = JSONField(null=True)

    class Meta:
        abstract = True
        ordering = ["-create_time"]


class ProfileRelatedLog(Log):
    profile = models.ForeignKey("profiles.Profile", verbose_name="登陆用户", on_delete=models.CASCADE)

    class Meta:
        abstract = True


class GeneralLog(Log):
    """通用操作日志"""

    status = models.CharField("状态", max_length=16, choices=OperationStatus.get_choices())


class ApiRequest(Log):
    """API 请求日志"""

    uri = models.CharField("请求 URI", max_length=64)
    time_cost = models.FloatField("请求耗时")
    method = models.CharField("请求方法", max_length=32)
    status = models.IntegerField("Http状态码")


class LogIn(ProfileRelatedLog):
    """登陆记录"""

    is_success = models.BooleanField("是否成功登陆", default=True)
    reason = models.CharField(
        "登陆失败原因",
        max_length=32,
        choices=LogInFailReason.get_choices(),
        null=True,
        blank=True,
    )

    objects = LogInManager()

    class Meta:
        ordering = ["-create_time"]
        get_latest_by = "create_time"

        index_together = [
            ["profile", "create_time"],
        ]


class ResetPassword(ProfileRelatedLog):
    """重置密码记录"""

    # 为 null 时，即为有登陆态的密码重置
    token = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, null=True)
    is_success = models.BooleanField("是否重置成功", default=False)
    password = EncryptField(default="")
    reason = models.CharField(
        "重置密码失败原因",
        max_length=32,
        choices=ResetPasswordFailReason.get_choices(),
        null=True,
        blank=True,
    )

    objects = ResetPasswordManager()

    def __str__(self):
        return f"{self.operator}-{self.token}"

    class Meta:
        ordering = ["-create_time"]
        get_latest_by = "create_time"
