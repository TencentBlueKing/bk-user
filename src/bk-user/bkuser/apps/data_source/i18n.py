# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
from django.utils.translation import gettext_lazy as _

from bkuser.plugins.constants import DataSourcePluginEnum

DATA_SOURCE_PLUGIN_NAMES = {
    DataSourcePluginEnum.LOCAL: _("本地数据源"),
    DataSourcePluginEnum.GENERAL: _("通用 HTTP 数据源"),
    DataSourcePluginEnum.LDAP: _("LDAP 数据源"),
}

DATA_SOURCE_PLUGIN_DESCRIPTIONS = {
    DataSourcePluginEnum.LOCAL: _("支持用户和部门的增删改查，以及用户的登录认证"),
    DataSourcePluginEnum.GENERAL: _(
        "支持对接通用 HTTP 数据源的插件，用户需要在服务方提供 `用户数据` 及 `部门数据` API"
    ),
    DataSourcePluginEnum.LDAP: _(
        "支持对接 LDAP 数据源的插件，用户需要提供符合 LDAP 协议的数据服务，如 OpenLDAP、Microsoft Active Directory 等"
    ),
}


def get_data_source_plugin_name(plugin) -> str:
    return str(DATA_SOURCE_PLUGIN_NAMES.get(plugin.id, plugin.name))


def get_data_source_plugin_description(plugin) -> str:
    return str(DATA_SOURCE_PLUGIN_DESCRIPTIONS.get(plugin.id, plugin.description))
