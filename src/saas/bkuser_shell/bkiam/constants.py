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


class PrincipalTypeEnum(AutoLowerEnum):
    USER = auto()


class ActionEnum(AutoLowerEnum):

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
    def get_action_by_category_type(cls, category_type: str) -> "ActionEnum":
        from bkuser_shell.categories.constants import CategoryTypeEnum

        return {  # type: ignore
            CategoryTypeEnum.LOCAL.value: cls.CREATE_LOCAL_CATEGORY,
            CategoryTypeEnum.LDAP.value: cls.CREATE_LDAP_CATEGORY,
            CategoryTypeEnum.MAD.value: cls.CREATE_MAD_CATEGORY,
        }[category_type]


class ResourceTypeEnum(AutoLowerEnum):
    FIELD = auto()
    CATEGORY = auto()
    DEPARTMENT = auto()
    PROFILE = auto()
