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

from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _


class ObjectTypeEnum(str, StructuredEnum):
    """操作对象类型"""

    DATA_SOURCE = EnumField("data_source", label=_("数据源"))
    IDP = EnumField("idp", label=_("认证源"))
    USER = EnumField("user", label=_("用户"))
    DEPARTMENT = EnumField("department", label=_("部门"))
    TENANT = EnumField("tenant", label=_("租户"))
    VIRTUAL_USER = EnumField("virtual_user", label=_("虚拟用户"))


class OperationEnum(str, StructuredEnum):
    """操作行为"""

    # 数据源
    CREATE_DATA_SOURCE = EnumField("create_data_source", label=_("创建数据源"))
    MODIFY_DATA_SOURCE = EnumField("modify_data_source", label=_("修改数据源"))
    DELETE_DATA_SOURCE = EnumField("delete_data_source", label=_("删除数据源"))
    SYNC_DATA_SOURCE = EnumField("sync_data_source", label=_("同步数据源"))
    # 认证源
    CREATE_IDP = EnumField("create_idp", label=_("创建认证源"))
    MODIFY_IDP = EnumField("modify_idp", label=_("修改认证源"))
    MODIFY_IDP_STATUS = EnumField("modify_idp_status", label=_("修改认证源状态"))
    # 用户
    CREATE_USER = EnumField("create_user", label=_("创建用户"))
    MODIFY_USER = EnumField("modify_user", label=_("修改用户信息"))
    DELETE_USER = EnumField("delete_user", label=_("删除用户"))
    MODIFY_USER_DEPARTMENT_RELATIONS = EnumField("modify_user_department_relations", label=_("修改用户所属部门"))
    MODIFY_USER_STATUS = EnumField("modify_user_status", label=_("修改用户状态"))
    MODIFY_USER_ACCOUNT_EXPIRED_AT = EnumField("modify_user_account_expired_at", label=_("修改用户账号过期时间"))
    MODIFY_USER_LEADERS = EnumField("modify_user_leaders", label=_("修改用户上级"))
    MODIFY_USER_PASSWORD = EnumField("modify_user_password", label=_("重置用户密码"))
    MODIFY_USER_EMAIL = EnumField("modify_user_email", label=_("修改用户邮箱"))
    MODIFY_USER_PHONE = EnumField("modify_user_phone", label=_("修改用户电话号码"))
    # 部门
    CREATE_DEPARTMENT = EnumField("create_department", label=_("创建部门"))
    MODIFY_DEPARTMENT = EnumField("modify_department", label=_("修改部门名称"))
    DELETE_DEPARTMENT = EnumField("delete_department", label=_("删除部门"))
    MODIFY_PARENT_DEPARTMENT = EnumField("modify_parent_department", label=_("修改上级部门"))
    # 租户
    CREATE_TENANT = EnumField("create_tenant", label=_("创建租户"))
    MODIFY_TENANT = EnumField("modify_tenant", label=_("修改租户信息"))
    DELETE_TENANT = EnumField("delete_tenant", label=_("删除租户"))
    MODIFY_TENANT_STATUS = EnumField("modify_tenant_status", label=_("修改租户状态"))
    CREATE_TENANT_REAL_MANAGER = EnumField("create_tenant_real_manager", label=_("创建租户实名管理员"))
    DELETE_TENANT_REAL_MANAGER = EnumField("delete_tenant_real_manager", label=_("删除租户实名管理员"))
    MODIFY_TENANT_ACCOUNT_VALIDITY_PERIOD_CONFIG = EnumField(
        "modify_tenant_account_validity_period_config", label=_("修改租户账户有效期配置")
    )
    # 虚拟用户
    CREATE_VIRTUAL_USER = EnumField("create_virtual_user", label=_("创建虚拟用户"))
    MODIFY_VIRTUAL_USER = EnumField("modify_virtual_user", label=_("修改虚拟用户信息"))
    DELETE_VIRTUAL_USER = EnumField("delete_virtual_user", label=_("删除虚拟用户"))
