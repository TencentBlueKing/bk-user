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

from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum

IDP_PLUGIN_NAMES = {
    BuiltinIdpPluginEnum.LOCAL: _("账密登录"),
    BuiltinIdpPluginEnum.WECOM: _("企业微信"),
}

IDP_PLUGIN_DESCRIPTIONS = {
    BuiltinIdpPluginEnum.LOCAL: _("使用本地 DB 数据源提供的用户名和密码进行认证"),
    BuiltinIdpPluginEnum.WECOM: _("使用腾讯企业微信进行企业身份认证"),
}


def get_idp_plugin_name(plugin) -> str:
    return str(IDP_PLUGIN_NAMES.get(plugin.id, plugin.name))


def get_idp_plugin_description(plugin) -> str:
    return str(IDP_PLUGIN_DESCRIPTIONS.get(plugin.id, plugin.description))
