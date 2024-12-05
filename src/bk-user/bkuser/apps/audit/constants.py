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

from blue_krill.data_types.enum import EnumField, StrStructuredEnum
from django.utils.translation import gettext_lazy as _


class ObjectTypeEnum(StrStructuredEnum):
    """操作对象类型"""

    DATA_SOURCE = EnumField("data_source", label=_("数据源"))
    IDP = EnumField("idp", label=_("认证源"))
    DATA_SOURCE_USER = EnumField("data_source_user", label=_("数据源用户"))
    TENANT_USER = EnumField("tenant_user", label=_("租户用户"))
    DATA_SOURCE_DEPARTMENT = EnumField("data_source_department", label=_("数据源部门"))
    TENANT_DEPARTMENT = EnumField("tenant_department", label=_("租户部门"))
    TENANT = EnumField("tenant", label=_("租户"))
    VIRTUAL_USER = EnumField("virtual_user", label=_("虚拟用户"))


class OperationEnum(StrStructuredEnum):
    """操作行为"""

    # 数据源
    CREATE_DATA_SOURCE = EnumField("create_data_source", label=_("创建数据源"))
    MODIFY_DATA_SOURCE = EnumField("modify_data_source", label=_("修改数据源"))
    DELETE_DATA_SOURCE = EnumField("delete_data_source", label=_("删除数据源"))
    SYNC_DATA_SOURCE = EnumField("sync_data_source", label=_("同步数据源"))

    # 认证源
    CREATE_IDP = EnumField("create_idp", label=_("创建认证源"))
    MODIFY_IDP = EnumField("modify_idp", label=_("修改认证源"))
    DELETE_IDP = EnumField("delete_idp", label=_("删除认证源"))

    # 用户
    CREATE_DATA_SOURCE_USER = EnumField("create_data_source_user", label=_("创建数据源用户"))
    CREATE_TENANT_USER = EnumField("create_tenant_user", label=_("创建租户用户"))
    CREATE_USER_DEPARTMENT = EnumField("create_user_department", label=_("创建用户-部门关系"))
    CREATE_COLLABORATION_TENANT_USER = EnumField("create_collaboration_tenant_user", label=_("创建协同租户用户"))

    MODIFY_DATA_SOURCE_USER = EnumField("modify_data_source_user", label=_("修改数据源用户"))
    MODIFY_TENANT_USER = EnumField("modify_tenant_user", label=_("修改租户用户"))
    MODIFY_USER_LEADER = EnumField("modify_user_leader", label=_("修改用户-上级关系"))
    MODIFY_USER_DEPARTMENT = EnumField("modify_user_department", label=_("修改用户-部门关系"))
    MODIFY_USER_STATUS = EnumField("modify_user_status", label=_("修改用户状态"))
    MODIFY_USER_ACCOUNT_EXPIRED_AT = EnumField("modify_user_account_expired_at", label=_("修改用户账号过期时间"))
    MODIFY_USER_PASSWORD = EnumField("modify_user_password", label=_("修改用户密码"))
    MODIFY_USER_EMAIL = EnumField("modify_user_email", label=_("修改用户邮箱"))
    MODIFY_USER_PHONE = EnumField("modify_user_phone", label=_("修改用户电话号码"))

    DELETE_DATA_SOURCE_USER = EnumField("delete_data_source_user", label=_("删除数据源用户"))
    DELETE_TENANT_USER = EnumField("delete_tenant_user", label=_("删除租户用户"))
    DELETE_USER_LEADER = EnumField("delete_user_leader", label=_("删除用户-上级关系"))
    DELETE_USER_DEPARTMENT = EnumField("delete_user_department", label=_("删除用户-部门关系"))
    DELETE_COLLABORATION_TENANT_USER = EnumField("delete_collaboration_tenant_user", label=_("删除协同租户用户"))

    # 部门
    CREATE_DATA_SOURCE_DEPARTMENT = EnumField("create_data_source_department", label=_("创建数据源部门"))
    CREATE_TENANT_DEPARTMENT = EnumField("create_tenant_department", label=_("创建租户部门"))
    CREATE_COLLABORATION_TENANT_DEPARTMENT = EnumField(
        "create_collaboration_tenant_department", label=_("创建协同租户部门")
    )
    CREATE_PARENT_DEPARTMENT = EnumField("create_parent_department", label=_("创建部门-父部门关系"))
    MODIFY_DATA_SOURCE_DEPARTMENT = EnumField("modify_data_source_department", label=_("修改数据源部门"))
    MODIFY_TENANT_DEPARTMENT = EnumField("modify_tenant_department", label=_("修改租户部门"))
    MODIFY_PARENT_DEPARTMENT = EnumField("modify_parent_department", label=_("修改部门-父部门关系"))
    DELETE_DATA_SOURCE_DEPARTMENT = EnumField("delete_data_source_department", label=_("删除数据源部门"))
    DELETE_TENANT_DEPARTMENT = EnumField("delete_tenant_department", label=_("删除租户部门"))
    DELETE_COLLABORATION_TENANT_DEPARTMENT = EnumField(
        "delete_collaboration_tenant_department", label=_("删除协同租户部门")
    )
    DELETE_PARENT_DEPARTMENT = EnumField("delete_parent_department", label=_("删除部门-父部门关系"))

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
    MODIFY_VIRTUAL_USER = EnumField("modify_virtual_user", label=_("修改虚拟用户"))
    DELETE_VIRTUAL_USER = EnumField("delete_virtual_user", label=_("删除虚拟用户"))
