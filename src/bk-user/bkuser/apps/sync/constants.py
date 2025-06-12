# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
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

import re

from blue_krill.data_types.enum import EnumField, StrStructuredEnum
from django.utils.translation import gettext_lazy as _

from bkuser.plugins.local.constants import USERNAME_REGEX as DATA_SOURCE_USERNAME_REGEX  # noqa: F401

EMAIL_REGEX = re.compile(r"^[\w.-]+@[\w.-]+\.[A-Za-z]{2,6}$")


class DataSourceSyncPeriodType(StrStructuredEnum):
    """数据源自动同步周期类型（单位）"""

    NEVER = EnumField("never", label=_("永不"))
    MINUTE = EnumField("minute", label=_("分钟"))
    HOUR = EnumField("hour", label=_("小时"))
    DAY = EnumField("day", label=_("天"))


class SyncTaskTrigger(StrStructuredEnum):
    """同步任务触发器枚举"""

    CRONTAB = EnumField("crontab", label=_("定时任务"))
    MANUAL = EnumField("manual", label=_("手动"))
    # 如：数据源同步完成信号触发租户数据同步
    SIGNAL = EnumField("signal", label=_("信号触发"))


class SyncLogLevel(StrStructuredEnum):
    """同步日志等级"""

    INFO = EnumField("INFO", label="INFO")
    WARNING = EnumField("WARNING", label="WARNING")
    ERROR = EnumField("ERROR", label="ERROR")


class SyncTaskStatus(StrStructuredEnum):
    """同步任务状态枚举"""

    PENDING = EnumField("pending", label=_("等待"))
    RUNNING = EnumField("running", label=_("执行中"))
    SUCCESS = EnumField("success", label=_("成功"))
    FAILED = EnumField("failed", label=_("失败"))


class SyncOperation(StrStructuredEnum):
    """同步操作枚举"""

    CREATE = EnumField("create", label=_("创建"))
    UPDATE = EnumField("update", label=_("更新"))
    DELETE = EnumField("delete", label=_("删除"))


class DataSourceSyncObjectType(StrStructuredEnum):
    """数据源同步数据类型枚举"""

    USER = EnumField("user", label=_("用户"))
    DEPARTMENT = EnumField("department", label=_("部门"))
    DEPARTMENT_RELATION = EnumField("department_relation", label=_("部门关系"))
    USER_LEADER_RELATION = EnumField("user_leader_relation", label=_("用户 Leader 关系"))
    USER_DEPARTMENT_RELATION = EnumField("user_department_relation", label=_("用户部门关系"))


class TenantSyncObjectType(StrStructuredEnum):
    """租户同步数据类型枚举"""

    USER = EnumField("user", label=_("用户"))
    DEPARTMENT = EnumField("department", label=_("部门"))
