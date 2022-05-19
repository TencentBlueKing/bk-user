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

from django.utils.translation import gettext_lazy as _

from bkuser_core.categories.constants import SyncStep
from bkuser_core.common.enum import AutoNameEnum

PLUGIN_NAME_SETTING_KEY = "plugin_name"
DYNAMIC_FIELDS_SETTING_KEY = "dynamic_fields_mapping"

SYNC_LOG_TEMPLATE_MAP = {
    (SyncStep.USERS, True): _("同步用户【{username}】成功"),
    (SyncStep.USERS, False): _("同步用户【{username}】失败, 失败原因: {error}"),
    (SyncStep.DEPARTMENTS, True): _("同步组织【{department}】成功"),
    (SyncStep.DEPARTMENTS, False): _("同步组织【{department}】失败"),
    (SyncStep.DEPT_USER_RELATIONSHIP, True): _("同步组织【{department}】与用户【{username}】的关联关系成功"),
    (SyncStep.DEPT_USER_RELATIONSHIP, False): _("同步组织【{department}】与用户【{username}】的关联关系失败, 失败原因: {error}"),
    (SyncStep.USERS_RELATIONSHIP, True): _("同步用户【{username}】上级成功"),
    (SyncStep.USERS_RELATIONSHIP, False): _("同步用户【{username}】上级失败, 失败原因: {error}"),
}


class HookType(AutoNameEnum):
    POST_SYNC = auto()
    PRE_SYNC = auto()
