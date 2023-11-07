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
import re

from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _

from bkuser.plugins.local.constants import USERNAME_REGEX as DATA_SOURCE_USERNAME_REGEX  # noqa: F401

EMAIL_REGEX = re.compile(r"^[\w.-]+@[\w.-]+\.[A-Za-z]{2,6}$")


class DataSourceSyncPeriod(int, StructuredEnum):
    """数据源自动同步周期"""

    NEVER = EnumField(0, label=_("从不"))
    PER_30_MIN = EnumField(30, label=_("每 30 分钟"))
    PER_1_HOUR = EnumField(60, label=_("每 1 小时"))
    PER_3_HOUR = EnumField(3 * 60, label=_("每 3 小时"))
    PER_6_HOUR = EnumField(6 * 60, label=_("每 6 小时"))
    PER_12_HOUR = EnumField(12 * 60, label=_("每 12 小时"))
    PER_1_DAY = EnumField(24 * 60, label=_("每 1 天"))
    PER_7_DAY = EnumField(7 * 24 * 60, label=_("每 7 天"))
    PER_30_DAY = EnumField(30 * 24 * 60, label=_("每 30 天"))


class SyncTaskTrigger(str, StructuredEnum):
    """同步任务触发器枚举"""

    CRONTAB = EnumField("crontab", label=_("定时任务"))
    MANUAL = EnumField("manual", label=_("手动"))
    # 如：数据源同步完成信号触发租户数据同步
    SIGNAL = EnumField("signal", label=_("信号触发"))


class SyncLogLevel(str, StructuredEnum):
    """同步日志等级"""

    INFO = EnumField("INFO", label="INFO")
    WARNING = EnumField("WARNING", label="WARNING")
    ERROR = EnumField("ERROR", label="ERROR")


class SyncTaskStatus(str, StructuredEnum):
    """同步任务状态枚举"""

    PENDING = EnumField("pending", label=_("等待"))
    RUNNING = EnumField("running", label=_("执行中"))
    SUCCESS = EnumField("success", label=_("成功"))
    FAILED = EnumField("failed", label=_("失败"))


class SyncOperation(str, StructuredEnum):
    """同步操作枚举"""

    CREATE = EnumField("create", label=_("创建"))
    UPDATE = EnumField("update", label=_("更新"))
    DELETE = EnumField("delete", label=_("删除"))


class DataSourceSyncObjectType(str, StructuredEnum):
    """数据源同步数据类型枚举"""

    USER = EnumField("user", label=_("用户"))
    DEPARTMENT = EnumField("department", label=_("部门"))
    USER_RELATION = EnumField("user_relation", label=_("用户关系"))
    DEPARTMENT_RELATION = EnumField("department_relation", label=_("部门关系"))


class TenantSyncObjectType(str, StructuredEnum):
    """租户同步数据类型枚举"""

    USER = EnumField("user", label=_("用户"))
    DEPARTMENT = EnumField("department", label=_("部门"))
