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
from enum import auto

from bkuser_shell.common.constants import AutoLowerEnum
from django.utils.translation import ugettext_lazy as _


class SyncStep(AutoLowerEnum):
    USERS = auto()
    DEPARTMENTS = auto()
    USERS_RELATIONSHIP = auto()
    DEPT_USER_RELATIONSHIP = auto()

    _choices_labels = (
        (USERS, _("用户数据更新")),
        (DEPARTMENTS, _("组织数据更新")),
        (USERS_RELATIONSHIP, _("用户间关系数据更新")),
        (DEPT_USER_RELATIONSHIP, _("用户和组织关系数据更新")),
    )


class SyncTaskType(AutoLowerEnum):
    MANUAL = auto()
    AUTO = auto()

    _choices_labels = ((MANUAL, _("手动导入")), (AUTO, _("定时同步")))


class SyncTaskStatus(AutoLowerEnum):
    SUCCESSFUL = auto()
    FAILED = auto()
    RUNNING = auto()

    _choices_labels = ((SUCCESSFUL, _("成功")), (FAILED, _("失败")), (RUNNING, _("同步中")))
