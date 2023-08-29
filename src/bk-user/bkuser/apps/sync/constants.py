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
from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _


class SyncTaskTrigger(str, StructuredEnum):
    """同步任务触发器枚举"""

    CRONTAB = EnumField("crontab", label=_("定时任务"))
    MANUAL = EnumField("manual", label=_("手动"))
    # TODO 补全所有触发场景
    # OTHER = EnumField("other", label=_("其他"))


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


class DataSourceSyncStepName(str, StructuredEnum):
    """数据源同步步骤枚举"""

    FETCH_DATA = EnumField("fetch_data", label=_("获取数据"))
    DATA_FORMAT = EnumField("data_format", label=_("数据格式化"))
    FIELD_MAPPING = EnumField("field_mapping", label=_("字段映射"))
    SAVE_DATA = EnumField("save_data", label=_("数据入库"))


class TenantSyncObjectType(str, StructuredEnum):
    """租户同步数据类型枚举"""

    USER = EnumField("user", label=_("用户"))
    DEPARTMENT = EnumField("department", label=_("部门"))


class TenantSyncStepName(str, StructuredEnum):
    """租户同步步骤枚举"""

    SAVE_DATA = EnumField("save_data", label=_("数据入库"))
