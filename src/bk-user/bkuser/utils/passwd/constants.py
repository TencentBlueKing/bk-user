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

# 最小密码长度，过小的下限会导致难以生成/设置合法的密码（最低不能低于 9）
MIN_PASSWORD_LENGTH = 10

# 最小的限制连续长度，过小的下限会导致难以生成/设置合法的密码（最低不能低于 3）
MIN_NOT_CONTINUOUS_COUNT = 3

# 弱密码词总长度占总密码长度的最大阈值，过高的阈值可能导致密码中包含过多的诸如 random, password 之类的弱密码常见词
MAX_WEAK_PASSWD_COMBINATION_THRESHOLD = 0.6


class ZxcvbnPattern(str, StructuredEnum):
    """密码片段匹配模式"""

    REPEAT = EnumField("repeat", label=_("重复"))
    DATE = EnumField("date", label=_("日期"))
    DICTIONARY = EnumField("dictionary", label=_("字典"))
    SEQUENCE = EnumField("sequence", label=_("序列"))
    REGEX = EnumField("regex", label=_("正则"))
    SPATIAL = EnumField("spatial", label=_("空间连续性"))
    BRUTEFORCE = EnumField("bruteforce", label=_("暴力破解"))
