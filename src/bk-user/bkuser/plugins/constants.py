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
from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _

# 非内置插件，必须以指定前缀开头
CUSTOM_PLUGIN_ID_PREFIX = "custom_"

# Logo 限制 64KB，过大的 logo 会导致性能下降，1024 * 1024 约 37KB
MAX_LOGO_SIZE = 64 * 1024


class DataSourcePluginEnum(str, StructuredEnum):
    """数据源插件枚举"""

    LOCAL = EnumField("local", label=_("本地数据源"))
    GENERAL = EnumField("general", label=_("通用 HTTP 数据源"))
    WECOM = EnumField("wecom", label=_("企业微信"))
    LDAP = EnumField("ldap", label=_("OpenLDAP"))
    MAD = EnumField("mad", label=_("MicrosoftActiveDirectory"))
