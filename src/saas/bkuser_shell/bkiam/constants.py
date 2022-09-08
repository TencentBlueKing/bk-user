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
from enum import Enum, auto

from django.utils.translation import ugettext_lazy as _

from bkuser_shell.common.constants import AutoLowerEnum


class CategoryTypeEnum(Enum):
    LOCAL = "local"
    MAD = "mad"
    LDAP = "ldap"
    CUSTOM = "custom"
    # 特殊的类型，仅在未解耦前桥接
    PLUGGABLE = "pluggable"

    _choices_labels = (
        (LOCAL, _("本地目录")),
        (MAD, _("Microsoft Active Directory")),
        (LDAP, _("LDAP")),
        (CUSTOM, _("自定义目录")),
        (PLUGGABLE, "可插拔目录"),
    )


class IAMAction(AutoLowerEnum):

    # 用户字段
    MANAGE_FIELD = auto()

    # 审计
    VIEW_AUDIT = auto()

    # 目录相关
    CREATE_LOCAL_CATEGORY = auto()
    CREATE_LDAP_CATEGORY = auto()
    CREATE_MAD_CATEGORY = auto()
    CREATE_CUSTOM_CATEGORY = auto()
    MANAGE_CATEGORY = auto()
    VIEW_CATEGORY = auto()

    # 部门
    CREATE_ROOT_DEPARTMENT = auto()
    MANAGE_DEPARTMENT = auto()

    # 部门下人员管理
    MANAGE_DEPARTMENT_PROFILES = auto()
    VIEW_DEPARTMENT = auto()

    @classmethod
    def get_action_by_category_type(cls, category_type: str) -> "IAMAction":
        return {  # type: ignore
            CategoryTypeEnum.LOCAL.value: cls.CREATE_LOCAL_CATEGORY,
            CategoryTypeEnum.LDAP.value: cls.CREATE_LDAP_CATEGORY,
            CategoryTypeEnum.MAD.value: cls.CREATE_MAD_CATEGORY,
        }[category_type]
