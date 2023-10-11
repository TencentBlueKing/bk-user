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


class DataSourcePluginEnum(str, StructuredEnum):
    """数据源插件枚举"""

    LOCAL = EnumField("local", label=_("本地数据源"))
    GENERAL = EnumField("general", label=_("通用 HTTP 数据源"))
    WECOM = EnumField("wecom", label=_("企业微信"))
    LDAP = EnumField("ldap", label=_("OpenLDAP"))
    MAD = EnumField("mad", label=_("MicrosoftActiveDirectory"))


class DataSourceSyncPeriod(int, StructuredEnum):
    """数据源自动同步周期"""

    PER_30_MIN = EnumField(30, label=_("每 30 分钟"))
    PER_1_HOUR = EnumField(60, label=_("每 1 小时"))
    PER_3_HOUR = EnumField(3 * 60, label=_("每 3 小时"))
    PER_6_HOUR = EnumField(6 * 60, label=_("每 6 小时"))
    PER_12_HOUR = EnumField(12 * 60, label=_("每 12 小时"))
    PER_1_DAY = EnumField(24 * 60, label=_("每 1 天"))
    PER_7_DAY = EnumField(7 * 24 * 60, label=_("每 7 天"))
    PER_30_DAY = EnumField(30 * 24 * 60, label=_("每 30 天"))
