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
from bkuser.plugins.ldap.constants import PageSize
from bkuser.plugins.ldap.models import (
    DataConfig,
    LDAPDataSourcePluginConfig,
    LeaderConfig,
    ServerConfig,
    UserGroupConfig,
)

# 通用 HTTP 数据源插件默认配置
DEFAULT_PLUGIN_CONFIG = LDAPDataSourcePluginConfig(
    server_config=ServerConfig(
        server_url="ldaps://bk.example.com:8389",
        bind_dn="cn=admin,ou=system_users,dc=bk,dc=example,dc=com",
        bind_password="******",
        base_dn="dc=bk,dc=example,dc=com",
        page_size=PageSize.CNT_100,
        request_timeout=30,
        retries=3,
    ),
    data_config=DataConfig(
        user_object_class="inetOrgPerson",
        user_search_filter="ou=company,dc=bk,dc=example,dc=com",
        dept_object_class="organizationalUnit",
        dept_search_filter="ou=company,dc=bk,dc=example,dc=com",
    ),
    user_group_config=UserGroupConfig(
        enabled=True,
        object_class="groupOfNames",
        search_filter="ou=company,dc=bk,dc=example,dc=com",
        group_name_field="cn",
        group_member_field="member",
    ),
    leader_config=LeaderConfig(
        enabled=True,
        leader_field="manager",
    ),
)
