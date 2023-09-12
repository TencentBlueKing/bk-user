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
import pytz
from blue_krill.data_types.enum import EnumField, FeatureFlag, FeatureFlagField, StructuredEnum
from django.utils.translation import gettext_lazy as _

TIME_ZONE_CHOICES = [(i, i) for i in list(pytz.common_timezones)]


class TenantFeatureFlag(FeatureFlag):  # type: ignore
    """租户特性标志"""

    USER_NUMBER_VISIBLE = FeatureFlagField(label=_("人员数量是否可见"), default=True)


class UserFieldDataType(str, StructuredEnum):
    """租户用户自定义字段数据类型"""

    STRING = EnumField("string", label=_("字符串"))
    NUMBER = EnumField("number", label=_("数字"))
    DATETIME = EnumField("datetime", label=_("日期时间"))
    ENUM = EnumField("enum", label=_("枚举"))
    MULTI_ENUM = EnumField("multi_enum", label=_("多选枚举"))
