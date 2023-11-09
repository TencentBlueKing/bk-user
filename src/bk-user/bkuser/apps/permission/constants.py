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
import logging

from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class UserRole(str, StructuredEnum):
    """用户角色"""

    SUPER_MANAGER = EnumField("super_manager", label=_("超级管理员"))
    TENANT_MANAGER = EnumField("tenant_manager", label=_("租户管理员"))
    NATURAL_USER = EnumField("natural_user", label=_("普通用户"))


class PermAction(str, StructuredEnum):
    """权限行为"""

    # TODO (su) 接入 IAM 时，需要评估是否细化 Action
    # 平台管理 - 超级管理员
    MANAGE_PLATFORM = EnumField("manage_platform", label=_("平台管理"))
    # 租户管理 - 租户管理员
    MANAGE_TENANT = EnumField("manage_tenant", label=_("租户管理"))
    # 平台使用 - 普通用户/自然人
    USE_PLATFORM = EnumField("use_platform", label=_("平台使用"))
